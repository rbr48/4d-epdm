#!/usr/bin/env python3
"""
compare_all_models.py
=====================
Head-to-head driver: NCD-LP, HB-DLP-SV, BVAR-MN, GBRT
under the same rolling-origin harness from evaluation.py.

Prints: per-horizon RMSE table, pooled RMSE ranking, DM tests vs ar1_fe,
         and the pre-registered verdict for each candidate.
"""
from __future__ import annotations
import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Local imports
from evaluation import rolling_origin, diebold_mariano, verdict, summarize, TARGET
from candidate_model import neoclassical_convergence_lp
from advanced_model import hb_dlp_sv
from bvar_minnesota import bvar_minnesota
from gbrt_model import gbrt_forecaster

HORIZONS = [1, 2, 3, 4, 5]


def load_panel() -> pd.DataFrame:
    p = Path(__file__).resolve().parent / "data" / "processed" / "panel_raw.csv"
    if not p.exists():
        raise SystemExit("Run data_layer.py first.")
    panel = pd.read_csv(p).dropna(subset=[TARGET])
    return panel


def main():
    panel = load_panel()
    print(f"Panel: {len(panel)} rows, {panel.iso.nunique()} countries, "
          f"{panel.year.min()}-{panel.year.max()}\n")

    candidates = {
        "ncd_lp":       neoclassical_convergence_lp,
        "hb_dlp_sv":    hb_dlp_sv,
        "bvar_mn":      bvar_minnesota,
        "gbrt":         gbrt_forecaster,
    }

    print("Running rolling-origin evaluation (this takes a few minutes)...")
    ev = rolling_origin(panel, candidates, horizons=HORIZONS)

    # Summary table
    s = summarize(ev)
    piv = s.pivot_table(index="h", columns="model", values="RMSE").round(4)
    print("\n== RMSE by horizon ==")
    print(piv.to_string())

    # Pooled RMSE
    pooled = ev.groupby("model")["sq"].mean().pow(0.5).sort_values()
    print("\n== Pooled RMSE (best first) ==")
    for m, v in pooled.items():
        print(f"  {m:24s} {v:.4f}")

    # DM tests vs ar1_fe
    print("\n== DM tests vs ar1_fe ==")
    for name in candidates:
        print(f"\n  {name}:")
        for h in HORIZONS:
            dm = diebold_mariano(ev, name, "ar1_fe", h)
            stat_str = f"{dm['stat']:.3f}" if np.isfinite(dm['stat']) else "N/A"
            p_str = f"{dm['p']:.4f}" if np.isfinite(dm['p']) else "N/A"
            print(f"    h={h}: stat={stat_str}, p={p_str}, better={dm['better']}")

    # Verdicts
    print("\n== Pre-registered verdicts ==")
    for name in candidates:
        v = verdict(ev, name, HORIZONS)
        tag = "PASS" if v["pass"] else "FAIL"
        print(f"  {name:24s}: {tag} -- {v['reason']}")
        print(f"    beats_every_benchmark: {v['beats_every_benchmark']}")
        print(f"    significant_horizons:  {v['horizons_significantly_better']}")

    # Save
    out_path = Path(__file__).resolve().parent / "outputs" / "compare_all_models.csv"
    out_path.parent.mkdir(exist_ok=True)
    ev.to_csv(out_path, index=False)
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
