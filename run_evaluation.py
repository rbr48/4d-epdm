#!/usr/bin/env python3
"""
Run Official Pre-Registered Evaluation for 4D Economic Power
============================================================

This script evaluates the candidate forecasting model:
    Neoclassical Convergence Local Projection (NCLP)
against the canonical pre-registered benchmarks.

It enforces:
  - 19 Rolling Origins (2001..2019)
  - 16 Economies
  - Horizons h = 1..5
  - Strict zero-leakage protocol
  - Evaluation via evaluation.py::verdict
"""

import os
import json
import numpy as np
import pandas as pd
from evaluation import rolling_origin, report, verdict
from candidate_model import neoclassical_convergence_lp

PANEL_PATH = "data/processed/panel_raw.csv"
OUTPUT_PATH = "outputs_candidate.csv"


def main():
    print("=" * 70)
    print("4D ECONOMIC POWER: PRE-REGISTERED OUT-OF-SAMPLE EVALUATION")
    print("=" * 70)

    if not os.path.exists(PANEL_PATH):
        raise FileNotFoundError(f"Panel data not found at {PANEL_PATH}")

    panel = pd.read_csv(PANEL_PATH).dropna(subset=["GDP_GROWTH"])
    print(f"Loaded panel: {len(panel)} rows across {panel['iso'].nunique()} economies.")

    forecasters = {
        "NCLP": neoclassical_convergence_lp
    }

    print("\nExecuting rolling-origin evaluation across 19 origins...")
    ev = rolling_origin(panel, forecasters, verbose=True)

    print(f"\nSaving full evaluation outputs to {OUTPUT_PATH}...")
    ev.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved {len(ev)} evaluation records to {OUTPUT_PATH}.")

    print("\n" + "=" * 70)
    print("OFFICIAL BENCHMARK REPORT & PRE-REGISTRATION VERDICT")
    print("=" * 70)
    report(ev, "NCLP")

    v = verdict(ev, "NCLP")
    print("\nMachine-readable verdict:")
    print(json.dumps(v, indent=2))

    if v["pass"]:
        print("\n>>> RESULT: SUCCESS -- PRE-REGISTRATION CRITERIA PASSED! <<<")
    else:
        print("\n>>> RESULT: FAIL -- PRE-REGISTRATION CRITERIA NOT MET <<<")

    return v


if __name__ == "__main__":
    main()
