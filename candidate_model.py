#!/usr/bin/env python3
"""
Neoclassical Convergence & Demographic Dividend Local Projection (NCD-LP)
==========================================================================

This module implements the official candidate forecasting model for the
4D Economic Power benchmark.

Econometric Architecture:
-------------------------
1. Short Horizon (h = 1) - Business Cycle Persistence Regime:
   At 1-year ahead horizons, business cycle persistence dominates. Transitory
   macroeconomic shocks persist according to an autoregressive process with
   country fixed effects:
       y_{i, t+1} = alpha_{i, 1} + rho_1 * y_{i, t} + epsilon_{i, t+1}
   Matches the optimal empirical persistence of the best short-horizon benchmark (ar1_fe).

2. Medium Horizons (h = 2..5) - Convergence & Demographic Dividend Regime:
   Over medium-term horizons (2 to 5 years), transitory business cycle
   persistence decays rapidly toward zero. Macroeconomic trajectory is anchored by:
     a) Neoclassical convergence distance: log GDP per capita in PPP terms relative
        to the global sample mean (Solow-Swan; Barro & Sala-i-Martin 1992).
     b) The Demographic Dividend: The age dependency ratio relative to global
        demographic structure, capturing the expansion or contraction of the
        productive working-age workforce (Bloom, Canning & Sevilla 2003).
   Specification:
       y_{i, t+h} = alpha_{i, h} + beta_{1, h} * (ln(GDP_PC_PPP_{i, t}) - mu_{log_gdppc})
                                 + beta_{2, h} * (DEPENDENCY_RATIO_{i, t} - mu_{dep_ratio})
                                 + epsilon_{i, t+h}
   Estimated directly via Direct Local Projections (Jordà 2005) with L2 Ridge
   shrinkage to prevent parameter over-fitting in small samples.

Structural No-Leakage Guarantee:
--------------------------------
At each origin T, the forecaster receives only observations with year <= T.
All transformations, global centering constants, country means, and Ridge
regressions are refit strictly on the training sample.
"""

import numpy as np
import pandas as pd

TARGET = "GDP_GROWTH"


def bench_ar1_fe_step1(train, origin):
    """
    AR(1) with country fixed effects for horizon h=1.
    """
    d = train.sort_values(["iso", "year"]).copy()
    d["lag"] = d.groupby("iso")[TARGET].shift(1)
    d = d.dropna(subset=[TARGET, "lag"])
    if len(d) < 30:
        m = train.groupby("iso")[TARGET].mean()
        return pd.DataFrame([{"iso": i, "h": 1, "pred": m.get(i, train[TARGET].mean())}
                             for i in train.iso.unique()])

    g = d.groupby("iso")
    yw = (d[TARGET] - g[TARGET].transform("mean")).to_numpy()
    xw = (d["lag"] - g["lag"].transform("mean")).to_numpy()
    rho = float(xw @ yw / max(xw @ xw, 1e-12))
    means = d.groupby("iso")[[TARGET, "lag"]].mean()

    last = train.sort_values("year").groupby("iso")[TARGET].last()
    out = []
    for iso in last.index:
        if iso not in means.index:
            continue
        alpha = float(means.loc[iso, TARGET] - rho * means.loc[iso, "lag"])
        y = float(last[iso])
        pred_val = alpha + rho * y
        out.append({"iso": iso, "h": 1, "pred": pred_val})
    return pd.DataFrame(out)


def neoclassical_convergence_lp(train: pd.DataFrame, origin: int, horizons: list,
                                l2_reg: float = 15.0) -> pd.DataFrame:
    """
    Neoclassical Convergence & Demographic Dividend Local Projection (NCD-LP) forecaster.

    Parameters:
    -----------
    train : pd.DataFrame
        Historical panel data strictly up to `origin`.
    origin : int
        Current forecast origin year (e.g. 2001..2019).
    horizons : list
        List of forecast horizons (e.g. [1, 2, 3, 4, 5]).
    l2_reg : float
        Ridge L2 penalty parameter for local projections (default: 15.0).

    Returns:
    --------
    pd.DataFrame with columns ['iso', 'h', 'pred'].
    """
    out = []
    d = train.sort_values(["iso", "year"]).copy()

    # Precompute log GDP per capita and dependency ratio
    if "GDP_PC_PPP" in d.columns:
        d["log_gdppc"] = np.log(d["GDP_PC_PPP"])
    else:
        d["log_gdppc"] = np.nan

    if "DEPENDENCY_RATIO" in d.columns:
        d["dep_ratio"] = d["DEPENDENCY_RATIO"]
    else:
        d["dep_ratio"] = np.nan

    features = ["log_gdppc", "dep_ratio"]
    last_rows = d.sort_values("year").groupby("iso").last()
    all_isos = list(d["iso"].unique())

    for h in horizons:
        if h == 1:
            # Short-horizon (h=1): Autoregressive persistence dominates
            preds_h1 = bench_ar1_fe_step1(train, origin)
            out.extend(preds_h1.to_dict(orient="records"))
            continue

        # Medium-horizon (h >= 2): Local projection with convergence & demographics
        d_h = d.copy()
        d_h["target_h"] = d_h.groupby("iso")[TARGET].shift(-h)

        sub = d_h.dropna(subset=["target_h"] + features)

        if len(sub) < 30:
            m = train.groupby("iso")[TARGET].mean()
            global_m = float(train[TARGET].mean())
            for iso in all_isos:
                out.append({"iso": iso, "h": h, "pred": float(m.get(iso, global_m))})
            continue

        # Country fixed effects demeaning for target
        g = sub.groupby("iso")
        yw = (sub["target_h"] - g["target_h"].transform("mean")).to_numpy()

        # Global mean centering for structural predictors
        means_dict = {}
        X_cols = []
        for f in features:
            m_f = float(sub[f].mean())
            means_dict[f] = m_f
            X_cols.append((sub[f] - m_f).to_numpy())

        X = np.column_stack(X_cols)
        p_dim = X.shape[1]
        penalty = l2_reg * np.eye(p_dim)

        try:
            beta = np.linalg.solve(X.T @ X + penalty, X.T @ yw)
        except np.linalg.LinAlgError:
            beta = np.zeros(p_dim)

        means_y = sub.groupby("iso")["target_h"].mean()
        global_target_m = float(sub["target_h"].mean())

        for iso in last_rows.index:
            alpha = float(means_y.get(iso, global_target_m))
            pred_val = alpha
            for j, f in enumerate(features):
                val = float(last_rows.loc[iso, f]) if (f in last_rows.columns and pd.notna(last_rows.loc[iso, f])) else means_dict[f]
                pred_val += beta[j] * (val - means_dict[f])
            out.append({"iso": iso, "h": h, "pred": pred_val})

    return pd.DataFrame(out)


if __name__ == "__main__":
    import sys
    from evaluation import rolling_origin, report

    print("Loading processed panel...")
    panel = pd.read_csv("data/processed/panel_raw.csv").dropna(subset=[TARGET])

    print("Running rolling origin evaluation of NCD-LP model...")
    ev = rolling_origin(panel, {"NCD-LP": neoclassical_convergence_lp}, verbose=True)

    print("\nEvaluation complete. Full report:")
    report(ev, "NCD-LP")
