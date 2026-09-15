#!/usr/bin/env python3
"""
Hyperparameter L2 Regularization Sensitivity Audit for NCD-LP
============================================================
This script tests whether l2_reg=15.0 was chosen by trial-and-error
or if the model's advantage over the pre-registered AR(1)+FE benchmark
is invariant across an entire broad regularization basin.

Evaluates against:
- Toughest benchmark: ar1_fe (pooled RMSE 2.9286)
- Diebold-Mariano test with Harvey-Leybourne-Newbold small sample correction
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from evaluation import rolling_origin, diebold_mariano
from candidate_model import neoclassical_convergence_lp

PANEL_PATH = Path("data/processed/panel_raw.csv")

def main():
    panel = pd.read_csv(PANEL_PATH).dropna(subset=["GDP_GROWTH"])
    l2_values = [0.01, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 15.0, 20.0, 30.0, 50.0, 100.0, 200.0]

    forecasters = {}
    for l2 in l2_values:
        name = f"NCD_LP_{l2}"
        def make_fn(val):
            return lambda train, origin, horizons: neoclassical_convergence_lp(train, origin, horizons, l2_reg=val)
        forecasters[name] = make_fn(l2)

    print("Running rolling origin across 19 origins for all l2 values...")
    ev = rolling_origin(panel, forecasters, verbose=False)

    bench = "ar1_fe"
    bench_rmse = (ev[ev["model"] == bench]["sq"].mean()) ** 0.5

    results = []
    for l2 in l2_values:
        name = f"NCD_LP_{l2}"
        cand_rmse = (ev[ev["model"] == name]["sq"].mean()) ** 0.5
        
        # Test DM vs ar1_fe at all horizons h=1..5
        dm_results = {}
        for h in [1, 2, 3, 4, 5]:
            dm = diebold_mariano(ev, name, bench, h)
            dm_results[h] = dm

        # Check DM at h=3
        dm_h3 = dm_results[3]
        sig_h = [h for h, d in dm_results.items() if d["p"] < 0.05 and d["better"] == name]

        results.append({
            "l2_reg": l2,
            "pooled_rmse": round(cand_rmse, 4),
            "diff_vs_ar1": round(cand_rmse - bench_rmse, 4),
            "beats_ar1": cand_rmse < bench_rmse,
            "dm_h3_stat": round(dm_h3["stat"], 3),
            "dm_h3_p": round(dm_h3["p"], 4),
            "sig_horizons": sig_h,
            "pass_prereg": bool(cand_rmse < bench_rmse and len(sig_h) > 0)
        })

    df = pd.DataFrame(results)
    out_csv = Path("outputs/l2_sensitivity_audit.csv")
    df.to_csv(out_csv, index=False)

    print("\n" + "=" * 80)
    print("HYPERPARAMETER L2 REGULARIZATION SENSITIVITY AUDIT")
    print("=" * 80)
    print(df.to_string(index=False))
    print("=" * 80)

    pass_df = df[df["pass_prereg"] == True]
    n_pass = len(pass_df)
    n_total = len(l2_values)
    print(f"\nAUDIT VERDICT: {n_pass} / {n_total} hyperparameter values meet pre-registered criteria.")
    if n_pass > 0:
        print(f"Lambda range that meets criteria: {pass_df['l2_reg'].min()} to {pass_df['l2_reg'].max()}")
        if n_pass == n_total:
            print("Conclusion: l2_reg=15.0 is NOT a knife-edge cherry-pick. The result is structural and stable.")
        else:
            print(f"Conclusion: {n_pass}/{n_total} values meet the bar. Sensitivity is partial.")
    else:
        print("Conclusion: No hyperparameter value meets pre-registered criteria.")

if __name__ == "__main__":
    main()
