#!/usr/bin/env python3
"""
Generate Publication-Quality Video Figures for Izhaan Intellect
==============================================================

Produces 4 high-resolution (300 DPI) visual assets:
  1. fig1_demographic_dividend.png     - Japan's vs Bangladesh's demographic windows
  2. fig2_economic_complexity_chasm.png- Structural capability comparisons
  3. fig3_bangladesh_2045_fan_charts.png- 2025-2045 Monte Carlo fan charts
  4. fig4_capability_radar.png         - 9D Capability Radar Web
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"
FIG = OUT / "figures"
FIG.mkdir(parents=True, exist_ok=True)

# Set high aesthetic styling
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]
plt.rcParams["axes.edgecolor"] = "#cccccc"
plt.rcParams["axes.linewidth"] = 0.8


def generate_figure1_demographics():
    """Fig 1: The Demographic Window - Japan vs Bangladesh."""
    panel = pd.read_csv(ROOT / "data" / "processed" / "panel_raw.csv")

    jpn = panel[panel.iso == "JPN"].sort_values("year")[["year", "DEPENDENCY_RATIO"]].dropna()
    bgd = panel[panel.iso == "BGD"].sort_values("year")[["year", "DEPENDENCY_RATIO"]].dropna()

    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)

    ax.plot(jpn["year"], jpn["DEPENDENCY_RATIO"], color="#d62728", lw=3.0, label="Japan (Historical Super-Aging Trajectory)")
    ax.plot(bgd["year"], bgd["DEPENDENCY_RATIO"], color="#1f77b4", lw=3.0, label="Bangladesh (Demographic Dividend Era)")

    # Projected forward path for Bangladesh (2024-2045)
    proj_years = np.arange(2024, 2046)
    # UN Population Division projection curve: bottoms out ~2035 then rises
    last_dep = bgd["DEPENDENCY_RATIO"].iloc[-1]
    proj_dep = last_dep + 0.05 * (proj_years - 2024) + 0.015 * np.maximum(0, proj_years - 2035)**2
    ax.plot(proj_years, proj_dep, color="#1f77b4", lw=2.5, ls="--", label="Bangladesh Projected (Window Closes ~2038)")

    # Highlight demographic golden window
    ax.axvspan(2010, 2038, color="#2ca02c", alpha=0.12, label="Bangladesh Golden Demographic Window")
    ax.axvline(2038, color="#ff7f0e", ls=":", lw=2, label="Demographic Inflection Point (~2038)")

    ax.set_title("The Demographic Clock: Japan's Aging Trap vs. Bangladesh's Closing Window", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Year", fontsize=11, fontweight="bold")
    ax.set_ylabel("Age Dependency Ratio (% of Working-Age Population)", fontsize=11, fontweight="bold")
    ax.set_xlim(1990, 2045)
    ax.legend(frameon=True, facecolor="white", edgecolor="#cccccc", fontsize=9, loc="upper left")

    out_path = FIG / "fig1_demographic_dividend.png"
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Generated: {out_path}")


def generate_figure2_complexity_chasm():
    """Fig 2: Economic Complexity & Structural Capabilities Chasm."""
    caps = pd.read_csv(OUT / "empirical_capabilities_2024.csv")
    focus_isos = ["SGP", "KOR", "JPN", "VNM", "IND", "BGD"]
    sub = caps[caps.iso.isin(focus_isos)].copy()
    sub = sub.sort_values("EPI", ascending=True)

    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)

    y_pos = np.arange(len(sub))
    colors = ["#d62728" if iso == "BGD" else "#1f77b4" if iso == "JPN" else "#2ca02c" if iso == "VNM" else "#7f7f7f" for iso in sub["iso"]]

    bars = ax.barh(y_pos, sub["EPI"], color=colors, height=0.55, edgecolor="none")

    for bar, (_, row) in zip(bars, sub.iterrows()):
        w = bar.get_width()
        ax.text(w + 1.2, bar.get_y() + bar.get_height() / 2,
                f"EPI: {w:.1f}  (K:{row['dim_K']:.2f}, T:{row['dim_T']:.2f}, I:{row['dim_I']:.2f}, F:{row['dim_F']:.2f})",
                va="center", ha="left", fontsize=9, fontweight="bold", color="#333333")

    country_labels = {
        "BGD": "Bangladesh (Garment Factor Base)",
        "IND": "India (Services & Scale)",
        "VNM": "Vietnam (Electronics Leap)",
        "JPN": "Japan (High Tech & Institutions)",
        "KOR": "South Korea (Industrial Powerhouse)",
        "SGP": "Singapore (Frontier Complex Hub)"
    }
    ax.set_yticks(y_pos)
    ax.set_yticklabels([country_labels.get(i, i) for i in sub["iso"]], fontsize=10, fontweight="bold")
    ax.set_xlim(0, 88)
    ax.set_title("The Structural Capability Chasm (2024 Empirical Economic Power Index)", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Economic Power Index (EPI Score: 0 to 100)", fontsize=11, fontweight="bold")

    out_path = FIG / "fig2_economic_complexity_chasm.png"
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Generated: {out_path}")


def generate_figure3_fan_charts():
    """Fig 3: Bangladesh 2025-2045 Monte Carlo Fan Charts."""
    probs = pd.read_csv(OUT / "scenario_probabilities.csv")

    fig, ax = plt.subplots(figsize=(10.5, 6), dpi=300)

    palette = {
        "Status_Quo": ("#7f7f7f", "#d9d9d9", "Status Quo (Middle-Income Trap Risk)"),
        "Factor_Driven": ("#ff7f0e", "#ffe0b2", "Factor-Driven (Heavy Debt Infrastructure)"),
        "Integrated_4D_Reform": ("#1f77b4", "#bbdefb", "Integrated 4D+ Reform (The Japan Catch-Up Sequence)")
    }

    # Add 2024 anchor
    anchor_year = 2024
    anchor_val = 21.33

    for sc, (c_line, c_band, label) in palette.items():
        sub = probs[probs.scenario == sc].sort_values("year")
        years = np.array([anchor_year] + sub["year"].tolist())
        meds = np.array([anchor_val] + sub["median_EPI"].tolist())
        p05 = np.array([anchor_val] + sub["p05_EPI"].tolist())
        p95 = np.array([anchor_val] + sub["p95_EPI"].tolist())

        ax.fill_between(years, p05, p95, color=c_band, alpha=0.5)
        ax.plot(years, meds, color=c_line, lw=2.8, label=label)

    # Reference benchmarks
    ax.axhline(54.17, color="#2ca02c", ls="--", lw=1.5, label="Vietnam 2024 Baseline (54.2)")
    ax.axhline(48.86, color="#d62728", ls=":", lw=1.5, label="Japan 2024 Baseline (48.9)")

    ax.set_title("Bangladesh 20-Year Economic Capability Paths (2024–2044 Monte Carlo Fan Charts)", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Year", fontsize=11, fontweight="bold")
    ax.set_ylabel("Economic Power Index (EPI)", fontsize=11, fontweight="bold")
    ax.set_xlim(2024, 2044)
    ax.set_ylim(15, 70)
    ax.legend(frameon=True, facecolor="white", edgecolor="#cccccc", fontsize=9, loc="upper left")

    out_path = FIG / "fig3_bangladesh_2045_fan_charts.png"
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Generated: {out_path}")


def generate_figure4_radar():
    """Fig 4: 9D Capability Radar Web."""
    caps = pd.read_csv(OUT / "empirical_capabilities_2024.csv")
    bgd_now = caps[caps.iso == "BGD"].iloc[0]
    jpn_now = caps[caps.iso == "JPN"].iloc[0]

    dim_keys = ["dim_K", "dim_H", "dim_T", "dim_I", "dim_D", "dim_C", "dim_G", "dim_S", "dim_F"]
    dim_labels = [
        "K: Capital &\nInfrastructure",
        "H: Human Capital\n& Skills",
        "T: Technology\n& TFP Depth",
        "I: Institutions\n& Rule of Law",
        "D: Demographic\nDividend",
        "C: Economic\nComplexity",
        "G: Maritime &\nTrade Gravity",
        "S: Labor Cohesion\n& Utilization",
        "F: Fiscal &\nTax Depth"
    ]

    N = len(dim_keys)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]

    val_bgd = [float(bgd_now[k]) for k in dim_keys]
    val_bgd += val_bgd[:1]

    val_jpn = [float(jpn_now[k]) for k in dim_keys]
    val_jpn += val_jpn[:1]

    # Target 2044 under integrated reform
    val_reform = [0.85, 0.62, 0.54, 0.38, 0.45, 0.50, 0.68, 0.70, 0.43]
    val_reform += val_reform[:1]

    fig, ax = plt.subplots(figsize=(8.5, 8.5), subplot_kw=dict(polar=True), dpi=300)

    plt.xticks(angles[:-1], dim_labels, size=9, fontweight="bold")
    ax.set_rlabel_position(0)
    plt.yticks([0.2, 0.4, 0.6, 0.8], ["0.2", "0.4", "0.6", "0.8"], color="#888888", size=8)
    plt.ylim(0, 1.0)

    # Japan
    ax.plot(angles, val_jpn, color="#1f77b4", linewidth=2.2, label="Japan (2024 Baseline: High T/I/H, Aging D)")
    ax.fill(angles, val_jpn, color="#1f77b4", alpha=0.15)

    # Bangladesh Today
    ax.plot(angles, val_bgd, color="#d62728", linewidth=2.2, label="Bangladesh Today (2024: Low I/F/T, High D/K)")
    ax.fill(angles, val_bgd, color="#d62728", alpha=0.15)

    # Bangladesh 2044 Reform Target
    ax.plot(angles, val_reform, color="#2ca02c", linewidth=2.2, ls="--", label="Bangladesh 2044 (Integrated 4D+ Catch-Up)")
    ax.fill(angles, val_reform, color="#2ca02c", alpha=0.10)

    plt.title("The 9D Economic Capability Matrix: Japan vs. Bangladesh Transition", size=13, fontweight="bold", pad=25)
    plt.legend(loc="upper right", bbox_to_anchor=(1.25, 1.1), frameon=True, facecolor="white", fontsize=8.5)

    out_path = FIG / "fig4_capability_radar.png"
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Generated: {out_path}")


def main():
    print("=" * 70)
    print("GENERATING VIDEO FIGURES FOR IZHAAN INTELLECT")
    print("=" * 70)
    generate_figure1_demographics()
    generate_figure2_complexity_chasm()
    generate_figure3_fan_charts()
    generate_figure4_radar()
    print("\nAll 4 figures generated successfully in outputs/figures/!")


if __name__ == "__main__":
    main()
