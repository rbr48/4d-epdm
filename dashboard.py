"""
4D-EPDM: Interactive Policy Simulator & Capability Visualizer
============================================================
Streamlit Web Dashboard for exploring Bangladesh's 2025-2045 development trajectories,
adversarial macro-shocks (2026 LDC Graduation, Banking NPL Freeze),
and 4D+ structural reform packages.

Launch via:
    streamlit run dashboard.py
"""

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="4D-EPDM: Bangladesh 2025-2045 Policy Simulator",
    page_icon="📈",
    layout="wide"
)

# Header & Overview
st.title("🏛️ 4D-EPDM: National Economic Capability Simulator (2025–2045)")
st.markdown("""
*Based on **"Japan’s Rise as an Economic Superpower and a Validated Dual-Engine Development Architecture for Bangladesh"**.*  
This interactive application simulates 20-year structural capability trajectories across **9 dimensions** 
under empirical convergence dynamics, stochastic shocks, and customizable reform levers.
""")

# Sidebar: Policy Levers & Shocks
st.sidebar.header("🛠️ Policy Levers (2025–2045)")

tax_reform = st.sidebar.slider(
    "1. Fiscal Mobilization (ΔF per year)",
    min_value=0.000, max_value=0.030, value=0.022, step=0.002,
    help="Expands tax-to-GDP ratio from 7.6% to 15-16% by 2035 via digital customs and automated VAT."
)

port_logistics = st.sidebar.slider(
    "2. Maritime Gravity & Matarbari (ΔG per year)",
    min_value=0.000, max_value=0.025, value=0.018, step=0.002,
    help="Matarbari deep-sea port and Bay of Bengal regional transit hub integration."
)

complexity_leap = st.sidebar.slider(
    "3. Product Space Diversification (ΔC per year)",
    min_value=0.000, max_value=0.025, value=0.016, step=0.002,
    help="Industrial policy transition from basic garments into electronics, APIs, and light engineering."
)

human_capital = st.sidebar.slider(
    "4. Technical & Institutional Reform (ΔH & ΔI)",
    min_value=0.000, max_value=0.020, value=0.012, step=0.002,
    help="German/Japanese dual vocational education and meritocratic governance institutionalization."
)

st.sidebar.markdown("---")
st.sidebar.header("⚡ Adversarial Shock Regimes")

shock_ldc = st.sidebar.checkbox(
    "2026 LDC Graduation Tariff Cliff",
    value=True,
    help="Loss of EU EBA tariff preferences and trade friction starting in 2026 (t=2)."
)

shock_npl = st.sidebar.checkbox(
    "Banking Sector NPL & Credit Freeze",
    value=False,
    help="Contraction of private sector credit intermediation due to non-performing loans."
)

shock_climate = st.sidebar.checkbox(
    "Compound Climate & Logistics Disruptions",
    value=False,
    help="Severe river port siltation and weather shocks suppressing capital efficiency."
)

num_paths = st.sidebar.select_slider(
    "Monte Carlo Paths",
    options=[1000, 2500, 5000, 10000],
    value=5000
)

# Simulation Engine
DIMENSIONS = ["K", "H", "T", "I", "D", "C", "G", "S", "F"]
WEIGHTS = np.array([0.15, 0.15, 0.15, 0.15, 0.10, 0.10, 0.05, 0.05, 0.10])
BGD_2024 = np.array([0.61, 0.38, 0.26, 0.04, 0.53, 0.18, 0.36, 0.45, 0.07])
JAP_1970 = np.array([0.72, 0.78, 0.65, 0.70, 0.82, 0.75, 0.58, 0.65, 0.50])

years = np.arange(2025, 2045)
horizon = len(years)

# Construct Policy Delta Vector
delta_policy = np.zeros(9)
delta_policy[8] = tax_reform        # Fiscal F
delta_policy[6] = port_logistics    # Gravity G
delta_policy[5] = complexity_leap   # Complexity C
delta_policy[1] = human_capital     # Human H
delta_policy[3] = human_capital     # Inst I
delta_policy[0] = human_capital * 0.5  # Capital K

# Shocks Vector
delta_shock = np.zeros(9)
sigma_base = 0.008

if shock_ldc:
    delta_shock[5] -= 0.010  # C shock
    delta_shock[6] -= 0.008  # G shock
    delta_shock[8] -= 0.005  # F shock
    sigma_base = max(sigma_base, 0.012)

if shock_npl:
    delta_shock[0] -= 0.012  # K shock
    delta_shock[8] -= 0.015  # F shock
    sigma_base = max(sigma_base, 0.014)

if shock_climate:
    delta_shock[0] -= 0.008  # K
    delta_shock[6] -= 0.010  # G
    sigma_base = max(sigma_base, 0.016)

# Execute Simulation
np.random.seed(42)
trajectories = np.zeros((num_paths, horizon, 9))
trajectories[:, 0, :] = BGD_2024

for t in range(horizon - 1):
    current = trajectories[:, t, :]
    u_t = np.random.normal(0, sigma_base, size=(num_paths, 9))
    
    # Apply discrete shock at t=2 (year 2026)
    shock_effect = delta_shock if t >= 1 else np.zeros(9)
    
    # Autonomous convergence drift toward global frontier
    theta_drift = 0.005 * (1.0 - current)
    
    # Demographic clock closing after 2038 (t > 13)
    if t > 13:
        u_t[:, 4] -= 0.012
        
    next_s = current + delta_policy + shock_effect + theta_drift + u_t
    trajectories[:, t + 1, :] = np.clip(next_s, 0.01, 0.99)

# Calculate EPI
epi_paths = 100.0 * np.prod(trajectories ** WEIGHTS, axis=2)
p10 = np.percentile(epi_paths, 10, axis=0)
p50 = np.percentile(epi_paths, 50, axis=0)
p90 = np.percentile(epi_paths, 90, axis=0)

median_2044 = p50[-1]
p_target = np.mean(epi_paths[:, -1] >= 50.0) * 100

# Layout: Key Metrics Display
col1, col2, col3, col4 = st.columns(4)
col1.metric("2024 Baseline EPI", "21.33", "Low Capability")
col2.metric("2044 Projected Median EPI", f"{median_2044:.2f}", f"{median_2044 - 21.33:+.2f}")
col3.metric("90% Confidence Interval", f"[{p10[-1]:.1f}, {p90[-1]:.1f}]")
col4.metric("P(EPI ≥ 50 / High-Income)", f"{p_target:.1f}%", "Takeoff Probability")

# Visualizations Row
tab1, tab2 = st.tabs(["📈 20-Year Fan Chart Trajectory", "🕸️ 9D Capability Radar Matrix"])

with tab1:
    fig, ax = plt.subplots(figsize=(10, 4.5), dpi=150)
    ax.fill_between(years, p10, p90, color="#1f77b4", alpha=0.2, label="90% Confidence Interval")
    ax.fill_between(years, np.percentile(epi_paths, 25, axis=0), np.percentile(epi_paths, 75, axis=0), color="#1f77b4", alpha=0.35, label="50% Interquartile Band")
    ax.plot(years, p50, color="#0b3c5d", lw=2.5, label="Median Simulated Trajectory")
    
    # Benchmarks
    ax.axhline(50.0, color="#d9534f", linestyle="--", lw=1.5, label="Industrial Takeoff Frontier (EPI=50)")
    ax.axhline(54.17, color="#5cb85c", linestyle=":", lw=1.5, label="Vietnam 2024 (54.17)")
    ax.axhline(21.33, color="gray", linestyle="--", lw=1.0, label="Bangladesh 2024 Baseline")
    
    ax.set_title("Bangladesh 2025–2045 Simulated Capability Trajectory", fontsize=12, fontweight="bold")
    ax.set_xlabel("Year")
    ax.set_ylabel("Economic Power Index (EPI, 0–100)")
    ax.set_ylim(10, 75)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(loc="upper left", fontsize=8)
    st.pyplot(fig)

with tab2:
    labels = ["Capital (K)", "Human (H)", "Tech (T)", "Institutions (I)", "Demographics (D)", "Complexity (C)", "Gravity (G)", "Social (S)", "Fiscal (F)"]
    num_vars = len(labels)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]
    
    bgd_2044_median = np.median(trajectories[:, -1, :], axis=0).tolist()
    bgd_2044_median += bgd_2044_median[:1]
    
    bgd_2024_vals = BGD_2024.tolist() + [BGD_2024[0]]
    jap_1970_vals = JAP_1970.tolist() + [JAP_1970[0]]
    
    fig2, ax2 = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True), dpi=150)
    ax2.plot(angles, bgd_2024_vals, color="#e74c3c", lw=2, label="Bangladesh 2024 (EPI: 21.3)")
    ax2.fill(angles, bgd_2024_vals, color="#e74c3c", alpha=0.15)
    
    ax2.plot(angles, bgd_2044_median, color="#2980b9", lw=2.5, label=f"Simulated 2044 (EPI: {median_2044:.1f})")
    ax2.fill(angles, bgd_2044_median, color="#2980b9", alpha=0.2)
    
    ax2.plot(angles, jap_1970_vals, color="#27ae60", linestyle="--", lw=1.8, label="Japan 1970 Benchmark")
    
    ax2.set_xticks(angles[:-1])
    ax2.set_xticklabels(labels, size=8)
    ax2.set_ylim(0, 1.0)
    ax2.set_title("9D Structural Capabilities: Baseline vs 2044", fontsize=11, fontweight="bold", pad=20)
    ax2.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1), fontsize=8)
    st.pyplot(fig2)

# Policy Conclusion Box
if median_2044 >= 50.0:
    st.success(f"🎉 **Takeoff Regime Achieved**: With Median EPI of **{median_2044:.1f}**, Bangladesh neutralizes external shocks and converges with industrialized Southeast Asian peers.")
elif median_2044 >= 35.0:
    st.warning(f"⚠️ **Moderate Growth / Trapping Risk**: Median EPI of **{median_2044:.1f}** leaves Bangladesh vulnerable to the middle-income trap as the demographic dividend closes ~2038.")
else:
    st.error(f"🚨 **Stagnation / Lost Decades**: Median EPI of **{median_2044:.1f}** indicates unmitigated post-2026 LDC shocks or credit contraction, halting structural catch-up.")

st.markdown("---")
st.caption("Izhaan Intellect Research Series | 4D-EPDM Pre-Registered Replication Suite | https://github.com/rbr48/4d-epdm")
