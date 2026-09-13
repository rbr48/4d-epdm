#!/usr/bin/env python3
"""
Evaluation harness. WRITTEN AND RUN BEFORE ANY MODEL EXISTS.

This ordering is the central lesson from the project this replaces. There, a large
estimator apparatus was built first and its predictive claim was tested last; when finally
tested it lost to a country mean at every horizon, and the entire structure turned out to
have been solving identification problems for a specification the data reject. Here the
bar is set, the benchmarks are implemented, and the test is executable before a single
line of the candidate model is written.

WHAT THIS ENFORCES
  * A forecaster receives ONLY `train` (rows with year <= origin). It cannot see the
    future because the future is not passed to it. Leakage is prevented structurally, not
    by discipline.
  * Every parameter is refit at every origin, including any normalisation, feature
    scaling, or variable selection. Fitting those once on the full sample is the most
    common silent leak in panel forecasting.
  * The benchmarks are real contenders, not straw men. On annual GDP growth for this kind
    of panel a country mean and a random walk are genuinely hard to beat, and the previous
    model lost to both.
  * Significance is tested, not eyeballed: Diebold-Mariano with a Newey-West correction of
    order h-1, computed on time-averaged loss differentials so that cross-sectional
    dependence between these 16 economies does not inflate the statistic.

FORECASTER CONTRACT
    def forecaster(train: DataFrame, origin: int, horizons: list) -> DataFrame
        returns columns ['iso', 'h', 'pred']
    `train` holds every column of the panel but only rows with year <= origin.
"""

import numpy as np
import pandas as pd
from scipy import stats

TARGET = "GDP_GROWTH"


# ===========================================================================
# BENCHMARKS -- deliberately strong
# ===========================================================================

def bench_random_walk(train, origin, horizons):
    """Last observed value, carried forward. The Meese-Rogoff benchmark."""
    last = train.sort_values("year").groupby("iso")[TARGET].last()
    return pd.DataFrame([{"iso": i, "h": h, "pred": v}
                         for i, v in last.items() for h in horizons])


def bench_rw_drift(train, origin, horizons):
    """Last value plus the country's own average change through the origin."""
    out = []
    for iso, g in train.sort_values("year").groupby("iso"):
        s = g[TARGET].dropna()
        if len(s) < 3:
            continue
        last, drift = float(s.iloc[-1]), float(np.mean(np.diff(s.to_numpy())))
        for h in horizons:
            out.append({"iso": iso, "h": h, "pred": last + drift * h})
    return pd.DataFrame(out)


def bench_country_mean(train, origin, horizons):
    """The country's historical mean growth. Beat the previous model at every horizon."""
    m = train.groupby("iso")[TARGET].mean()
    return pd.DataFrame([{"iso": i, "h": h, "pred": v}
                         for i, v in m.items() for h in horizons])


def bench_pooled_mean(train, origin, horizons):
    """The panel-wide mean -- maximal pooling, zero country information."""
    m = float(train[TARGET].mean())
    return pd.DataFrame([{"iso": i, "h": h, "pred": m}
                         for i in train.iso.unique() for h in horizons])


def bench_ar1_fe(train, origin, horizons):
    """AR(1) with country fixed effects, iterated forward."""
    d = train.sort_values(["iso", "year"]).copy()
    d["lag"] = d.groupby("iso")[TARGET].shift(1)
    d = d.dropna(subset=[TARGET, "lag"])
    if len(d) < 30:
        return bench_country_mean(train, origin, horizons)
    g = d.groupby("iso")
    yw = (d[TARGET] - g[TARGET].transform("mean")).to_numpy()
    xw = (d["lag"] - g["lag"].transform("mean")).to_numpy()
    rho = float(xw @ yw / max(xw @ xw, 1e-12))
    means = d.groupby("iso")[[TARGET, "lag"]].mean()
    out = []
    last = train.sort_values("year").groupby("iso")[TARGET].last()
    for iso in last.index:
        if iso not in means.index:
            continue
        alpha = float(means.loc[iso, TARGET] - rho * means.loc[iso, "lag"])
        y = float(last[iso])
        for h in range(1, max(horizons) + 1):
            y = alpha + rho * y
            if h in horizons:
                out.append({"iso": iso, "h": h, "pred": y})
    return pd.DataFrame(out)


BENCHMARKS = {
    "random_walk": bench_random_walk,
    "rw_drift": bench_rw_drift,
    "country_mean": bench_country_mean,
    "pooled_mean": bench_pooled_mean,
    "ar1_fe": bench_ar1_fe,
}


# ===========================================================================
# ROLLING-ORIGIN EVALUATION
# ===========================================================================

def rolling_origin(panel, forecasters, horizons=(1, 2, 3, 4, 5),
                   min_train_years=12, verbose=True):
    """
    Evaluate every forecaster over every feasible origin.

    `forecasters` maps name -> callable following the contract. Benchmarks are added
    automatically so a candidate can never be scored without them present.
    """
    horizons = list(horizons)
    panel = panel.sort_values(["iso", "year"]).copy()
    years = np.sort(panel["year"].unique())
    origins = [int(y) for y in years
               if (y - years[0] + 1) >= min_train_years and y + max(horizons) <= years[-1]]
    if not origins:
        raise ValueError(f"No feasible origins: need {min_train_years} training years "
                         f"plus {max(horizons)} for evaluation, panel spans "
                         f"{years[0]}-{years[-1]}.")

    allf = {**BENCHMARKS, **forecasters}
    if verbose:
        print(f"Rolling origin: {len(origins)} origins ({origins[0]}..{origins[-1]}), "
              f"horizons {horizons}, {len(allf)} forecasters")

    rows = []
    for origin in origins:
        train = panel[panel["year"] <= origin]
        future = panel[(panel["year"] > origin) &
                       (panel["year"] <= origin + max(horizons))]
        actual = {(r.iso, int(r.year - origin)): getattr(r, TARGET)
                  for r in future.itertuples() if pd.notna(getattr(r, TARGET))}
        for name, fn in allf.items():
            try:
                pred = fn(train.copy(), origin, horizons)
            except Exception as e:
                if verbose:
                    print(f"  {name} failed at origin {origin}: {type(e).__name__}: {e}")
                continue
            if pred is None or len(pred) == 0:
                continue
            for p in pred.itertuples():
                key = (p.iso, int(p.h))
                if key not in actual or not np.isfinite(p.pred):
                    continue
                a = actual[key]
                rows.append({"origin": origin, "iso": p.iso, "h": int(p.h),
                             "model": name, "actual": a, "pred": float(p.pred),
                             "err": float(p.pred) - a,
                             "sq": (float(p.pred) - a) ** 2,
                             "abs": abs(float(p.pred) - a)})
    return pd.DataFrame(rows)


def summarize(ev):
    """RMSE / MAE / bias by model and horizon, plus ratios against the random walk."""
    s = (ev.groupby(["model", "h"])
           .agg(RMSE=("sq", lambda x: float(np.sqrt(x.mean()))),
                MAE=("abs", "mean"), bias=("err", "mean"), n=("actual", "size"))
           .reset_index())
    base = s[s.model == "random_walk"].set_index("h")["RMSE"]
    s["vs_RW"] = s.apply(lambda r: r.RMSE / base.get(r.h, np.nan), axis=1)
    return s


# ===========================================================================
# DIEBOLD-MARIANO
# ===========================================================================

def diebold_mariano(ev, model_a, model_b, h, loss="sq"):
    """
    Test whether model_a's loss differs significantly from model_b's at horizon h.

    Loss differentials are averaged ACROSS COUNTRIES first, then treated as a time series
    of length equal to the number of origins. Pooling all country-horizon observations as
    if independent would treat 16 economies moving together in 2009 and 2020 as 16
    independent pieces of evidence and badly overstate significance.

    Newey-West with lag h-1 handles the overlap that h-step forecasts induce.
    Negative statistic => model_a has LOWER loss (is better).
    """
    a = ev[(ev.model == model_a) & (ev.h == h)][["origin", "iso", loss]]
    b = ev[(ev.model == model_b) & (ev.h == h)][["origin", "iso", loss]]
    m = a.merge(b, on=["origin", "iso"], suffixes=("_a", "_b"))
    if len(m) < 8:
        return {"stat": np.nan, "p": np.nan, "n": len(m), "better": None}

    d = (m.groupby("origin")
           .apply(lambda g: g[f"{loss}_a"].mean() - g[f"{loss}_b"].mean(),
                  include_groups=False)
           .to_numpy())
    n = len(d)
    if n < 4:
        return {"stat": np.nan, "p": np.nan, "n": n, "better": None}
    dbar = float(d.mean())
    dc = d - dbar
    gamma0 = float(dc @ dc / n)
    var = gamma0
    for lag in range(1, int(h)):
        if lag >= n:
            break
        cov = float(dc[lag:] @ dc[:-lag] / n)
        var += 2.0 * (1.0 - lag / h) * cov
    var = max(var, 1e-12)
    stat = dbar / np.sqrt(var / n)
    # Harvey-Leybourne-Newbold small-sample correction
    corr = np.sqrt(max((n + 1 - 2 * h + h * (h - 1) / n) / n, 1e-9))
    stat *= corr
    p = float(2 * (1 - stats.t.cdf(abs(stat), df=n - 1)))
    return {"stat": float(stat), "p": p, "n": n,
            "better": (model_a if dbar < 0 else model_b) if p < 0.05 else "neither"}


def verdict(ev, candidate, horizons=(1, 2, 3, 4, 5), alpha=0.05):
    """
    PRE-REGISTERED SUCCESS CRITERION.

    The candidate PASSES only if, pooled across horizons, it has lower RMSE than EVERY
    benchmark, and beats the single toughest benchmark with Diebold-Mariano p < alpha.
    Anything weaker -- winning at one horizon, winning on average without significance,
    winning only against a benchmark nobody would use -- is reported as a FAIL.

    This function is the arbiter. It is written before the model exists precisely so that
    it cannot be adjusted afterwards to accommodate a disappointing result.
    """
    pooled = (ev.groupby("model")["sq"].mean().pow(0.5).sort_values())
    if candidate not in pooled.index:
        return {"pass": False, "reason": f"{candidate} produced no forecasts",
                "pooled_rmse": pooled.to_dict()}

    benches = [m for m in pooled.index if m != candidate]
    beats_all = all(pooled[candidate] < pooled[b] for b in benches)
    toughest = min(benches, key=lambda b: pooled[b])

    tests = {}
    for h in horizons:
        tests[int(h)] = diebold_mariano(ev, candidate, toughest, h)
    sig = [h for h, t in tests.items()
           if np.isfinite(t["p"]) and t["p"] < alpha and t["better"] == candidate]

    return {
        "pass": bool(beats_all and len(sig) > 0),
        "candidate": candidate,
        "pooled_rmse": {k: round(float(v), 4) for k, v in pooled.items()},
        "beats_every_benchmark": bool(beats_all),
        "toughest_benchmark": toughest,
        "dm_vs_toughest": {h: {"stat": round(t["stat"], 3) if np.isfinite(t["stat"]) else None,
                               "p": round(t["p"], 4) if np.isfinite(t["p"]) else None,
                               "better": t["better"]} for h, t in tests.items()},
        "horizons_significantly_better": sig,
        "reason": ("passes" if beats_all and sig else
                   "does not beat every benchmark" if not beats_all else
                   "beats benchmarks but not significantly"),
    }


def report(ev, candidate=None, horizons=(1, 2, 3, 4, 5)):
    s = summarize(ev)
    piv = s.pivot_table(index="h", columns="model", values="RMSE").round(3)
    print("\nRMSE by horizon:")
    print(piv.to_string())
    pooled = ev.groupby("model")["sq"].mean().pow(0.5).sort_values()
    print("\nPooled RMSE (best first):")
    for m, v in pooled.items():
        print(f"  {m:22s} {v:.4f}")
    if candidate:
        v = verdict(ev, candidate, horizons)
        print(f"\n{'=' * 62}")
        print(f"VERDICT for '{candidate}': {'PASS' if v['pass'] else 'FAIL'} -- {v['reason']}")
        print(f"  beats every benchmark: {v['beats_every_benchmark']}")
        print(f"  toughest benchmark:    {v['toughest_benchmark']}")
        for h, t in v["dm_vs_toughest"].items():
            print(f"  DM h={h}: stat {t['stat']}, p {t['p']}, better: {t['better']}")
        print("=" * 62)
        return v
    return None


if __name__ == "__main__":
    from pathlib import Path
    p = Path(__file__).resolve().parent / "data" / "processed" / "panel_raw.csv"
    if not p.exists():
        raise SystemExit("Run data_layer.py first.")
    panel = pd.read_csv(p)
    panel = panel.dropna(subset=[TARGET])
    print(f"Panel: {len(panel)} rows, {panel.iso.nunique()} countries, "
          f"{panel.year.min()}-{panel.year.max()}\n")
    print("Benchmarks only -- establishing the bar BEFORE any model exists.")
    ev = rolling_origin(panel, {})
    report(ev)
    ev.to_csv(Path(__file__).resolve().parent / "outputs_baseline.csv", index=False)
