#!/usr/bin/env python3
"""
Extended Evaluation Suite for 4D-EPDM: HB-DLP-SV
================================================
Comprehensive evaluation addressing critical gaps in macro panel forecasting:
  1. Full Predictive Density Scoring: CRPS, Gaussian Log Score, and PIT Uniformity (KS test).
  2. Multi-Horizon Diebold-Mariano Tests with Bonferroni multiple-comparison correction.
  3. Adversarial Placebo Permutation Falsification (shuffling convergence & demographics).
  4. Per-Country Disaggregated RMSE (transparently auditing Bangladesh vs. others).
  5. Leave-One-Country-Out (LOO) Robustness Audit across all 16 economies.
"""
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

from evaluation import rolling_origin, diebold_mariano, verdict
from candidate_model import neoclassical_convergence_lp
from advanced_model import hb_dlp_sv_density, hb_dlp_sv

OUT = Path("outputs")
OUT.mkdir(exist_ok=True)
HORIZONS = [1, 2, 3, 4, 5]


# ---------------------------------------------------------------------------
# 1. Density Scores & Calibration Diagnostics
# ---------------------------------------------------------------------------

def crps_gaussian(y: float, mu: float, sigma: float) -> float:
    """Closed-form Continuous Ranked Probability Score (CRPS) for Gaussian predictive density."""
    sigma = max(float(sigma), 1e-6)
    z = (y - mu) / sigma
    return float(sigma * (z * (2 * stats.norm.cdf(z) - 1) + 2 * stats.norm.pdf(z) - 1 / np.sqrt(np.pi)))


def log_score_gaussian(y: float, mu: float, sigma: float) -> float:
    """Gaussian negative log predictive density score (smaller is better)."""
    sigma = max(float(sigma), 1e-6)
    return float(-stats.norm.logpdf(y, loc=mu, scale=sigma))


def evaluate_with_density(panel: pd.DataFrame, model_fn) -> pd.DataFrame:
    """Rolling-origin evaluation capturing full predictive distributions (mu, sigma)."""
    rows = []
    years = np.sort(panel["year"].unique())
    origins = [int(y) for y in years
               if (y - years[0] + 1) >= 12 and y + max(HORIZONS) <= years[-1]]

    for origin in origins:
        train = panel[panel["year"] <= origin]
        future = panel[(panel["year"] > origin) &
                       (panel["year"] <= origin + max(HORIZONS))]
        actual = {(r.iso, int(r.year - origin)): r.GDP_GROWTH
                  for r in future.itertuples() if pd.notna(r.GDP_GROWTH)}
        
        pred = model_fn(train, origin, HORIZONS)
        for p in pred.itertuples():
            key = (p.iso, int(p.h))
            if key not in actual:
                continue
            y = float(actual[key])
            mu = float(p.pred)
            sigma = max(float(p.sigma), 1e-6)
            sq_err = (y - mu) ** 2
            crps_val = crps_gaussian(y, mu, sigma)
            ls_val = log_score_gaussian(y, mu, sigma)
            pit_val = float(stats.norm.cdf((y - mu) / sigma))

            rows.append({
                "origin": origin,
                "iso": p.iso,
                "h": int(p.h),
                "y": y,
                "mu": mu,
                "sigma": sigma,
                "sq": sq_err,
                "crps": crps_val,
                "ls": ls_val,
                "pit": pit_val
            })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 2. Multi-Horizon Diebold-Mariano Tests with Bonferroni Correction
# ---------------------------------------------------------------------------

def dm_all_horizons(ev: pd.DataFrame, cand: str, bench: str) -> pd.DataFrame:
    """Evaluate Diebold-Mariano tests across all horizons with Bonferroni correction."""
    print(f"\n=== Diebold-Mariano Significance: {cand} vs {bench} ===")
    alpha = 0.05
    results = []
    
    for h in HORIZONS:
        a = ev[(ev.model == cand) & (ev.h == h)]
        b = ev[(ev.model == bench) & (ev.h == h)]
        m = a.merge(b, on=["origin", "iso"], suffixes=("_a", "_b"))
        if len(m) < 8:
            continue
        
        d = (m.groupby("origin")
               .apply(lambda g: g.sq_a.mean() - g.sq_b.mean(), include_groups=False)
               .to_numpy())
        n = len(d)
        dbar = d.mean()
        dc = d - dbar
        var = dc @ dc / n
        for lag in range(1, h):
            if lag < n:
                var += 2 * (1 - lag / h) * (dc[lag:] @ dc[:-lag] / n)
        stat = dbar / np.sqrt(max(var, 1e-12) / n)
        stat *= np.sqrt(max((n + 1 - 2 * h + h * (h - 1) / n) / n, 1e-9))
        p = float(2 * (1 - stats.t.cdf(abs(stat), df=n - 1)))
        
        results.append({
            "h": h,
            "stat": stat,
            "p": p,
            "sig_bonf": p < (alpha / len(HORIZONS)),
            "better": cand if dbar < 0 else bench
        })
    df = pd.DataFrame(results)
    print(df.round(4).to_string(index=False))
    return df


# ---------------------------------------------------------------------------
# 3. Adversarial Placebo Permutation Falsification
# ---------------------------------------------------------------------------

def placebo_permutation(panel: pd.DataFrame, model_fn, n_perm: int = 30, seed: int = 0):
    """
    Randomly permute convergence and dependency ratios within each country
    to assess whether macroeconomic predictive power reflects genuine causality
    or statistical noise.
    """
    rng = np.random.default_rng(seed)

    def eval_once(df: pd.DataFrame) -> float:
        rows = []
        years = np.sort(df["year"].unique())
        origins = [int(y) for y in years
                   if (y - years[0] + 1) >= 12 and y + max(HORIZONS) <= years[-1]]
        for origin in origins:
            train = df[df["year"] <= origin]
            future = df[(df["year"] > origin) & (df["year"] <= origin + max(HORIZONS))]
            actual = {(r.iso, int(r.year - origin)): r.GDP_GROWTH
                      for r in future.itertuples() if pd.notna(r.GDP_GROWTH)}
            pred = model_fn(train, origin, HORIZONS)
            for p in pred.itertuples():
                key = (p.iso, int(p.h))
                if key in actual:
                    rows.append((actual[key] - float(p.pred)) ** 2)
        return float(np.sqrt(np.mean(rows))) if rows else np.nan

    print("\nRunning Placebo Permutation Test...")
    real_rmse = eval_once(panel)
    null_dist = []
    
    for i in range(n_perm):
        d2 = panel.copy()
        for col in ("GDP_PC_PPP", "DEPENDENCY_RATIO"):
            if col in d2.columns:
                d2[col] = d2.groupby("iso")[col].transform(lambda x: rng.permutation(x.values))
        perm_rmse = eval_once(d2)
        null_dist.append(perm_rmse)
        if (i + 1) % 10 == 0:
            print(f"  Completed {i + 1}/{n_perm} permutations...")

    null_dist = np.array(null_dist)
    p_perm = float(np.mean(null_dist <= real_rmse))

    print(f"\n=== Placebo Permutation Falsification (N={n_perm}) ===")
    print(f"Real Model RMSE:        {real_rmse:.4f}")
    print(f"Null Mean RMSE (Noise): {null_dist.mean():.4f} +/- {null_dist.std():.4f}")
    print(f"Permutation p-value:    {p_perm:.4f}")
    if p_perm < 0.05:
        print(">> VERDICT: p < 0.05 -> Real structural features outperform permuted noise.")
    else:
        print(">> VERDICT: p >= 0.05 -> Shuffled features perform comparably (honest null result).")
    
    return real_rmse, null_dist, p_perm


# ---------------------------------------------------------------------------
# 4. Disaggregated Per-Country Audits & Leave-One-Out (LOO)
# ---------------------------------------------------------------------------

def per_country_rmse(ev: pd.DataFrame, h: int = 3) -> pd.DataFrame:
    """Disaggregate model performance across all individual economies."""
    sub = ev[ev.h == h]
    per = sub.groupby(["iso", "model"])["sq"].mean().pow(0.5).unstack().round(4)
    if "ar1_fe" in per.columns and "HB-DLP-SV" in per.columns:
        per["delta_vs_ar1"] = per["ar1_fe"] - per["HB-DLP-SV"]
        per = per.sort_values("delta_vs_ar1", ascending=False)
    print(f"\n=== Disaggregated Country RMSE at Horizon h={h} ===")
    print(per.to_string())
    return per


def leave_one_out(panel: pd.DataFrame, model_fn) -> pd.DataFrame:
    """Conduct leave-one-country-out panel sensitivity audit."""
    print("\n=== Leave-One-Country-Out (LOO) Sensitivity Audit ===")
    rows = []
    isos = sorted(panel["iso"].unique())
    
    for c in isos:
        sub = panel[panel["iso"] != c]
        ev = rolling_origin(sub, {"HB-DLP-SV": model_fn},
                            horizons=HORIZONS, verbose=False)
        v = verdict(ev, "HB-DLP-SV", horizons=HORIZONS)
        rows.append({
            "dropped_country": c,
            "overall_pass": v["pass"],
            "beats_every_benchmark": v["beats_every_benchmark"],
            "sig_horizons": v["horizons_significantly_better"]
        })
    df = pd.DataFrame(rows)
    print(df.to_string(index=False))
    return df


# ---------------------------------------------------------------------------
# 5. Master Driver
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    panel = pd.read_csv("data/processed/panel_raw.csv").dropna(subset=["GDP_GROWTH"])

    print("======================================================================")
    print("HB-DLP-SV: ADVANCED PROBABILISTIC & ECONOMETRIC EVALUATION")
    print("======================================================================")

    # 1. Density Evaluation
    print("\nStep 1: Evaluating Gaussian Predictive Densities...")
    ev_density = evaluate_with_density(panel, hb_dlp_sv_density)
    ev_density.to_csv(OUT / "hb_dlp_sv_density.csv", index=False)

    point_rmse = float(np.sqrt(ev_density["sq"].mean()))
    mean_crps = float(ev_density["crps"].mean())
    mean_ls = float(ev_density["ls"].mean())
    ks_stat, p_ks = stats.kstest(ev_density["pit"], "uniform")

    print(f"  Point RMSE (Pooled):  {point_rmse:.4f}")
    print(f"  CRPS (Pooled):        {mean_crps:.4f}")
    print(f"  Log Score (Pooled):   {mean_ls:.4f}")
    print(f"  PIT Uniformity KS:    stat={ks_stat:.4f}, p={p_ks:.4f}")
    if p_ks > 0.05:
        print("  >> Density Calibration: WELL CALIBRATED (PIT p > 0.05, cannot reject uniform)")
    else:
        print("  >> Density Calibration: Significant deviation from uniformity (PIT p <= 0.05)")

    # 2. Rolling-Origin Benchmark Comparison
    print("\nStep 2: Running 19-Origin Benchmark Competition...")
    ev = rolling_origin(
        panel,
        {
            "HB-DLP-SV": hb_dlp_sv,
            "NCD-LP": neoclassical_convergence_lp
        },
        horizons=HORIZONS,
        verbose=False
    )
    v_hb = verdict(ev, "HB-DLP-SV", horizons=HORIZONS)
    verdict_tag = "PASS" if v_hb["pass"] else "FAIL"
    print(f"\nVerdict for HB-DLP-SV: {verdict_tag}")
    print(f"  Beats every benchmark: {v_hb['beats_every_benchmark']}")
    print(f"  Horizons significantly better: {v_hb['horizons_significantly_better']}")

    # 3. Diebold-Mariano Multi-Horizon Tests
    dm_all_horizons(ev, "HB-DLP-SV", "ar1_fe")

    # 4. Disaggregated Per-Country Performance
    per_country_rmse(ev, h=3)

    # 5. Placebo Permutation Falsification
    placebo_permutation(panel, hb_dlp_sv, n_perm=30, seed=42)

    # 6. Leave-One-Country-Out Audit
    leave_one_out(panel, hb_dlp_sv)

    print("\n======================================================================")
    print("ADVANCED EVALUATION COMPLETE")
    print("======================================================================")
