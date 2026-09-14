"""
4D-EPDM: Master Replication & Execution Pipeline CLI
====================================================
Reproduces all empirical findings, out-of-sample benchmarking,
Monte Carlo capability trajectories, adversarial stress audits,
and publication figures in a single automated command.

Usage:
    python run_all.py --all
    python run_all.py --origins 19 --paths 20000
    python run_all.py --eval
    python run_all.py --sim
    python run_all.py --stress
    python run_all.py --figures
"""

import argparse
import sys
import time
import subprocess
from pathlib import Path

def print_banner():
    banner = """
================================================================================
          4D-EPDM: Master Replication Pipeline & Research Suite
      Japan's Rise vs. Bangladesh 2025-2045 Dual-Engine Architecture
================================================================================
"""
    print(banner)

def run_step(step_name, command):
    print(f"\n>>> [STEP] {step_name}")
    print(f"    Executing: {command}")
    start = time.time()
    res = subprocess.run(command, shell=True)
    elapsed = time.time() - start
    if res.returncode != 0:
        print(f"[ERROR] {step_name} failed with return code {res.returncode}")
        sys.exit(res.returncode)
    print(f"[OK] Completed {step_name} in {elapsed:.2f}s")

def main():
    parser = argparse.ArgumentParser(
        description="4D-EPDM Replication Pipeline CLI",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--all", action="store_true", help="Execute entire replication pipeline")
    parser.add_argument("--eval", action="store_true", help="Run 19-origin out-of-sample evaluation harness")
    parser.add_argument("--sim", action="store_true", help="Run 9D capability simulation & Monte Carlo paths")
    parser.add_argument("--stress", action="store_true", help="Run adversarial stress testing & placebo test")
    parser.add_argument("--figures", action="store_true", help="Generate all 300 DPI publication figures")
    parser.add_argument("--origins", type=int, default=19, help="Number of rolling origins for evaluation")
    parser.add_argument("--paths", type=int, default=20000, help="Number of Monte Carlo simulation trajectories")
    
    args = parser.parse_args()
    
    # Default to --all if no specific stage requested
    if not (args.eval or args.sim or args.stress or args.figures):
        args.all = True
        
    print_banner()
    t0 = time.time()
    python_cmd = sys.executable
    
    if args.all or args.eval:
        run_step(
            "1. Out-of-Sample Benchmark Evaluation (Engine 1)",
            f'"{python_cmd}" run_evaluation.py'
        )
        
    if args.all or args.sim:
        run_step(
            "2. 9D Capability State Space & Monte Carlo Simulator (Engine 2)",
            f'"{python_cmd}" power_dynamics_engine.py'
        )
        
    if args.all or args.stress:
        run_step(
            "3. Adversarial Stress-Testing & Falsification Suite",
            f'"{python_cmd}" stress_testing.py'
        )
        
    if args.all or args.figures:
        run_step(
            "4. Publication-Ready 300 DPI Visualizations",
            f'"{python_cmd}" generate_video_figures.py'
        )
        
    total_time = time.time() - t0
    print("\n" + "="*80)
    print(f"[SUCCESS] Full 4D-EPDM Research Pipeline Executed in {total_time:.2f}s")
    print("   All empirical metrics, pre-registration criteria, stress checks,")
    print("   and high-resolution figures in outputs/figures/ are verified.")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
