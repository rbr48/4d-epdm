#!/usr/bin/env python3
"""
Generate Publication-Quality Video Figures for Izhaan Intellect
==============================================================
Aligned to the 2026–2046 Economic Power Dynamics Horizon.

Produces 5 high-resolution (300 DPI, 16:9 aesthetic) visual assets:
  1. fig1_demographic_dividend.png      - Japan's aging trap vs Bangladesh's closing window (1990–2046)
  2. fig2_economic_complexity_chasm.png - Empirical structural capability comparison across 6 economies
  3. fig3_bangladesh_2045_fan_charts.png- 2026–2046 Monte Carlo capability fan charts (5,000 draws)
  4. fig4_capability_radar.png          - 9D Capability Radar Web (Japan vs Bangladesh 2026 vs 2046)
  5. fig5_macro_monetary_projections.png- 2026–2046 Dollar GDP (PPP), Tax Net & Export Fiscal Dividend
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
    """Fig 1: The Demographic Window - Japan vs Bangladesh (1990–2046)."""
    panel = pd.read_csv(ROOT / "data" / "processed" / "panel_raw.csv")

    jpn = panel[panel.iso == "JPN"].sort_values("year")[["year", "DEPENDENCY_RATIO"]].dropna()
    bgd = panel[panel.iso == "BGD"].sort_values("year")[["year", "DEPENDENCY_RATIO"]].dropna()

    fig, ax = plt.subplots(figsize=(11, 6), dpi=300)

    ax.plot(jpn["year"], jpn["DEPENDENCY_RATIO"], color="#d62728", lw=3.2, label="Japan (Historical Super-Aging Trajectory)")
    ax.plot(bgd["year"], bgd["DEPENDENCY_RATIO"], color="#1f77b4", lw=3.2, label="Bangladesh Observed (Demographic Dividend Era)")

    # Projected forward path for Bangladesh (2024-2046)
    proj_years = np.arange(2024, 2047)
    last_dep = bgd["DEPENDENCY_RATIO"].iloc[-1]
    proj_dep = last_dep + 0.04 * (proj_years - 2024) + 0.018 * np.maximum(0, proj_years - 2038)**2
    ax.plot(proj_years, proj_dep, color="#1f77b4", lw=2.6, ls="--", label="Bangladesh Projected (UN Median: Window Closes ~2038)")

    # Highlight demographic golden window
    ax.axvspan(2010, 2038, color="#2ca02c", alpha=0.12, label="Bangladesh Golden Demographic Window (2010–2038)")
    ax.axvline(2038, color="#ff7f0e", ls=":", lw=2.2, label="Demographic Inflection Point (~2038)")

    ax.set_title("The Demographic Clock: Japan's Aging Trap vs. Bangladesh's Closing Window (1990–2046)", fontsize=13, fontweight="bold", pad=15)
    ax.set_xlabel("Year", fontsize=11, fontweight="bold")
    ax.set_ylabel("Age Dependency Ratio (% of Working-Age Population)", fontsize=11, fontweight="bold")
    ax.set_xlim(1990, 2046)
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

    fig, ax = plt.subplots(figsize=(11, 6), dpi=300)

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
    ax.set_xlim(0, 92)
    ax.set_title("The Structural Capability Chasm (Empirical Economic Power Index Leaderboard)", fontsize=13, fontweight="bold", pad=15)
    ax.set_xlabel("Economic Power Index (EPI Score: 0 to 100)", fontsize=11, fontweight="bold")

    out_path = FIG / "fig2_economic_complexity_chasm.png"
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Generated: {out_path}")


def generate_figure3_fan_charts():
    """Fig 3: Bangladesh 2026–2046 Monte Carlo Fan Charts."""
    scenarios_path = OUT / "scenarios_2026_2046.csv"
    if not scenarios_path.exists():
        scenarios_path = OUT / "scenarios_2025_2045.csv"

    df = pd.read_csv(scenarios_path)

    fig, ax = plt.subplots(figsize=(11.5, 6.2), dpi=300)

    # Focus on three pivotal regimes
    sc_mapping = {
        "Baseline_Status_Quo": ("#6c757d", "#e9ecef", "Baseline Status Quo (Middle-Income Inertia)"),
        "Compound_Polycrisis": ("#dc3545", "#f8d7da", "Compound Polycrisis (LDC Cliff + NPL Freeze)"),
        "Resilient_4D_Response": ("#0d6efd", "#cfe2ff", "Resilient 4D+ Strategy (Japan Catch-Up Sequence)")
    }

    for sc_id, (c_line, c_band, label) in sc_mapping.items():
        sub = df[df.scenario == sc_id].sort_values("year")
        if sub.empty:
            continue
        years = sub["year"].values
        p50 = sub["p50"].values
        p05 = sub["p05"].values
        p95 = sub["p95"].values

        ax.fill_between(years, p05, p95, color=c_band, alpha=0.6)
        ax.plot(years, p50, color=c_line, lw=3.0, label=label)

    # Reference benchmarks
    ax.axhline(54.17, color="#198754", ls="--", lw=1.6, label="Vietnam Benchmark (54.2)")
    ax.axhline(48.86, color="#0dcaf0", ls=":", lw=1.6, label="Japan Baseline (48.9)")
    ax.axvline(2038, color="#ffc107", ls="-.", lw=1.4, label="Demographic Inflection (~2038)")

    ax.set_title("Bangladesh 20-Year Capability Projections (2026–2046 Monte Carlo Fan Charts: 5,000 Draws)", fontsize=13, fontweight="bold", pad=15)
    ax.set_xlabel("Horizon Year", fontsize=11, fontweight="bold")
    ax.set_ylabel("Economic Power Index (EPI)", fontsize=11, fontweight="bold")
    ax.set_xlim(2024, 2046)
    ax.set_ylim(15, 68)
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

    # Target 2046 under Resilient 4D+ Reform
    val_reform = [0.86, 0.65, 0.56, 0.42, 0.42, 0.52, 0.70, 0.72, 0.45]
    val_reform += val_reform[:1]

    fig, ax = plt.subplots(figsize=(8.5, 8.5), subplot_kw=dict(polar=True), dpi=300)

    plt.xticks(angles[:-1], dim_labels, size=9, fontweight="bold")
    ax.set_rlabel_position(0)
    plt.yticks([0.2, 0.4, 0.6, 0.8], ["0.2", "0.4", "0.6", "0.8"], color="#888888", size=8)
    plt.ylim(0, 1.0)

    # Japan
    ax.plot(angles, val_jpn, color="#1f77b4", linewidth=2.4, label="Japan (High T/I/H, Aging D)")
    ax.fill(angles, val_jpn, color="#1f77b4", alpha=0.15)

    # Bangladesh Today
    ax.plot(angles, val_bgd, color="#d62728", linewidth=2.4, label="Bangladesh Anchor (2026: Low I/F/T, High D/K)")
    ax.fill(angles, val_bgd, color="#d62728", alpha=0.15)

    # Bangladesh 2046 Reform Target
    ax.plot(angles, val_reform, color="#2ca02c", linewidth=2.4, ls="--", label="Bangladesh 2046 (Resilient 4D+ Catch-Up)")
    ax.fill(angles, val_reform, color="#2ca02c", alpha=0.10)

    plt.title("The 9D Economic Capability Matrix: Japan vs. Bangladesh Transition", size=13, fontweight="bold", pad=25)
    plt.legend(loc="upper right", bbox_to_anchor=(1.28, 1.12), frameon=True, facecolor="white", fontsize=8.5)

    out_path = FIG / "fig4_capability_radar.png"
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Generated: {out_path}")


def generate_figure5_monetary():
    """Fig 5: Macro Monetary & Dollar Projections (2026–2046)."""
    mon_path = OUT / "monetary_projections.csv"
    if not mon_path.exists():
        return

    df = pd.read_csv(mon_path)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=300)

    colors = {
        "Status_Quo": "#6c757d",
        "Factor_Driven": "#ff7f0e",
        "Integrated_4D_Reform": "#198754"
    }
    labels = {
        "Status_Quo": "Status Quo (Inertial)",
        "Factor_Driven": "Factor-Driven (Capex Heavy)",
        "Integrated_4D_Reform": "Integrated 4D+ Reform (Japan Sequence)"
    }

    for sc in ["Status_Quo", "Factor_Driven", "Integrated_4D_Reform"]:
        sub = df[df.scenario == sc].sort_values("year")
        if sub.empty:
            continue
        ax1.plot(sub["year"], sub["ppp_gdp_usd_b"], color=colors[sc], lw=2.8, label=labels[sc])
        ax2.plot(sub["year"], sub["tax_revenue_usd_b"], color=colors[sc], lw=2.8, label=labels[sc])

    # Left plot: PPP GDP
    ax1.set_title("Total GDP in Purchasing Power Parity (2026–2046)", fontsize=12, fontweight="bold")
    ax1.set_xlabel("Year", fontsize=10, fontweight="bold")
    ax1.set_ylabel("GDP PPP (USD Billions)", fontsize=10, fontweight="bold")
    ax1.legend(frameon=True, facecolor="white", edgecolor="#cccccc", fontsize=8.5, loc="upper left")
    ax1.set_xlim(2026, 2046)

    # Right plot: Fiscal Tax Revenue
    ax2.set_title("Annual Fiscal Tax Revenue (The Domestic Resource Mobilization Dividend)", fontsize=12, fontweight="bold")
    ax2.set_xlabel("Year", fontsize=10, fontweight="bold")
    ax2.set_ylabel("Fiscal Revenue (USD Billions)", fontsize=10, fontweight="bold")
    ax2.legend(frameon=True, facecolor="white", edgecolor="#cccccc", fontsize=8.5, loc="upper left")
    ax2.set_xlim(2026, 2046)

    out_path = FIG / "fig5_macro_monetary_projections.png"
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Generated: {out_path}")


def main():
    print("=" * 70)
    print("GENERATING VIDEO FIGURES FOR IZHAAN INTELLECT (2026–2046)")
    print("=" * 70)
    generate_figure1_demographics()
    generate_figure2_complexity_chasm()
    generate_figure3_fan_charts()
    generate_figure4_radar()
    generate_figure5_monetary()
    print("\nAll 5 video figures generated successfully in outputs/figures/!")


if __name__ == "__main__":
    main()
