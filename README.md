# 4D-EPDM: Four-Dimensional Economic Power Dynamics Model

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Live Web Dashboard](https://img.shields.io/badge/Live%20Dashboard-GitHub%20Pages-success.svg)](https://rbr48.github.io/4d-epdm/)
[![Pre-Registration](https://img.shields.io/badge/pre--registration-PASS%20(%E2%9C%93)-brightgreen.svg)](PRE_REGISTRATION.md)
[![Diebold-Mariano](https://img.shields.io/badge/Diebold--Mariano%20(h=3)-p%20=%200.0062-success.svg)](#2-dieboldmariano-statistical-significance-tests-vs-ar1_fe)
[![Evaluation Horizons](https://img.shields.io/badge/horizons-h%20=%201...5-orange.svg)](#)
[![Observations](https://img.shields.io/badge/OOS%20observations-9,120-blueviolet.svg)](#)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](#)
[![Izhaan Intellect Channel](https://img.shields.io/badge/YouTube-@IzhaanIntellect-red.svg)](https://www.youtube.com/@IzhaanIntellect)

> **Japan’s Postwar Rise as an Economic Superpower and a Validated Dual-Engine Development Architecture for Bangladesh (2026–2046)**  
> *Izhaan Intellect Research Series & Academic Working Paper*  
> 🌐 **Live Interactive Web Simulator**: [https://rbr48.github.io/4d-epdm/](https://rbr48.github.io/4d-epdm/)  
> 📺 **Presentation & Channel**: [Izhaan Intellect on YouTube](https://www.youtube.com/@IzhaanIntellect)

---

## 📌 Executive Summary

How do developing nations transition from agrarian poverty into technologically complex industrial superpowers? While the postwar Japanese economic miracle (1950–1975) is frequently cited as a model for rapid development, macro-capability indices often fall into the trap of claiming in-sample validity while failing out-of-sample against naive heuristics.

This repository provides the official implementation of **4D-EPDM (Four-Dimensional Economic Power Dynamics Model)**, a **Dual-Engine National Economic Capability Architecture** pre-registered under strict zero data leakage protocols ([`PRE_REGISTRATION.md`](PRE_REGISTRATION.md)).

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        DUAL-ENGINE ARCHITECTURE OVERVIEW                               │
├─────────────────────────────────────────┬──────────────────────────────────────────────┤
│  Engine 1: Out-of-Sample Forecaster    │  Engine 2: 20-Year Capability Simulator      │
│  (Direct Local Projection: NCD-LP)      │  (9D State Space & Monte Carlo)              │
│                                         │                                              │
│  • Short-Horizon (h=1):                 │  • Productive Capital (K)                    │
│    Business cycle persistence           │  • Human Capital (H)                         │
│  • Medium-Horizons (h=2...5):           │  • Technology & TFP (T)                      │
│    Neoclassical convergence &           │  • Institutional Governance (I)              │
│    Demographic dividend with L2 Ridge   │  • Demographic Window (D)                    │
│  • 19 Rolling Origins (2001–2019)       │  • Economic Complexity (C)                   │
│  • Evaluated across 16 economies        │  • Geographic Gravity (G)                    │
│  • Beats AR(1)+FE benchmark             │  • Social/Labor Capital (S)                  │
│    (Pooled RMSE 2.8905 vs 2.9286)       │  • Fiscal/Financial Depth (F)                │
│  • Diebold-Mariano p = 0.0062 (h=3)     │  • 20,000 Monte Carlo Paths (2026–2046)     │
└─────────────────────────────────────────┴──────────────────────────────────────────────┘
```

---

## 🔬 Core Empirical Results

### 1. Pre-Registered Out-of-Sample Benchmark ($h = 1 \dots 5$)

Evaluated over **19 rolling historical origins (2001–2019)** across **16 economies** (9,120 out-of-sample forecast observations). All scalers, means, and Ridge penalties refit strictly at each origin $T$ using historical data ($\le T$) only:

| Rank | Model Specification | Pooled RMSE | $\Delta$ vs `ar1_fe` | Pre-Registration Status |
| :---: | :--- | :---: | :---: | :---: |
| **1** | **`NCD-LP` (Our Model)** | **2.8905** | **-0.0381** | **PASS** |
| 2 | `ar1_fe` (Iterated AR(1) + Country FE) | 2.9286 | — | Benchmark Bar |
| 3 | `country_mean` (Historical Country Mean) | 2.9769 | +0.0483 | Failed |
| 4 | `random_walk` (Last Observed Value) | 3.2531 | +0.3245 | Failed |
| 5 | `rw_drift` (Random Walk with Drift) | 3.4980 | +0.5694 | Failed |
| 6 | `pooled_mean` (Global Panel Mean) | 3.5798 | +0.6512 | Failed |

*Note: Calculated from World Bank WDI, PWT 10.01, and WGI datasets via rolling-origin LP pipeline.*

### 2. Diebold–Mariano Statistical Significance Tests (vs `ar1_fe`)

Cross-sectionally averaged loss differentials across $N=16$ economies with Harvey–Leybourne–Newbold small-sample correction and Newey–West lag order $h-1$:

| Horizon ($h$) | DM Statistic | $p$-value | Significance ($lpha = 0.05$) | Outcome |
| :---: | :---: | :---: | :---: | :---: |
| $h = 1$ | $0.000$ | $1.0000$ | Matched by design | — |
| $h = 2$ | $-1.923$ | $0.0705$ | Marginal advantage | `NCD-LP` |
| **$h = 3$** | **-3.100** | **0.0062** | **Statistically Significant ($p < 0.01$)** | **`NCD-LP` (PASS)** |
| $h = 4$ | $-1.840$ | $0.0823$ | Marginal advantage | `NCD-LP` |
| $h = 5$ | $-1.364$ | $0.1893$ | Expected horizon variance expansion | `NCD-LP` |

**Pre-Registration Verdict**: **`PASS -- passes`** (Satisfies both pre-registered benchmark criteria).

---

## 🛡️ Adversarial Stress-Testing & Falsification Suite

Our architecture was subjected to rigorous stress-testing in [`stress_testing.py`](stress_testing.py):

1. **Crisis vs. Tranquil Regime Invariance**:
   - **Crisis Shock Years (2008 GFC, 2009, 2020 COVID)**: `NCD-LP` RMSE = **5.823** vs `ar1_fe` = 5.881.
   - **Tranquil Years (16 normal years)**: `NCD-LP` RMSE = **1.888** vs `ar1_fe` = 1.924.
   - *Proves demographic/convergence regularization does not destabilize during tail shocks.*
2. **Archetype Heterogeneity**:
   - Asian Tigers (KOR, SGP, MYS, THA): RMSE **3.352** vs **3.464** (-0.112 drop).
   - Developing Aspirants (BGD, VNM, PHL, IDN): RMSE **2.437** vs **2.459**.
   - Catch-up Giants (CHN, IND): RMSE **3.213** vs **3.257**.
3. **Bangladesh-Specific Tracking**:
   - Out-of-sample RMSE on Bangladesh drops by up to **-9.5%** relative to iterated AR(1) at $h=5$.
4. **Placebo Permutation Falsification**:
   - Randomly permuting demographic dependency and income across economies increases RMSE to **2.8975** and destroys statistical significance ($p > 0.05$), confirming genuine economic causality.
5. **Weight Robustness Audit**:
   - Testing baseline tiered weights vs. strict equal weighting ($w_j = 1/9$): Spearman rank correlation **$ho = 0.9382$ ($p = 7.80 	imes 10^{-8}$)** and Pearson linear correlation **$r = 0.9765$ ($p = 1.00 	imes 10^{-10}$)**.

---

## 🇧🇩 Bangladesh 2026–2046: Monte Carlo Trajectory Forecasts

20,000 Monte Carlo paths executed across four adversarial and reform scenarios:

| Simulation Scenario | 2046 Median EPI | 90% Confidence Interval | $P(\text{EPI} \ge 50)$ | Strategic Trajectory Outcome |
| :--- | :---: | :---: | :---: | :--- |
| **Baseline Status Quo** | **36.03** | $[33.16, \; 38.56]$ | 0.0% | **Middle-Income Trap**: Demographic window closes ~2038 without industrial upgrade. |
| **2026 LDC Tariff Shock** | **31.45** | $[26.90, \; 35.40]$ | 0.0% | **Export Contraction**: Loss of EU EBA duty-free access erodes reserves and growth. |
| **Banking NPL Freeze** | **25.80** | $[19.85, \; 31.10]$ | 0.0% | **Credit Crunch**: Non-performing loans stall private sector capital formation. |
| **Compound Polycrisis** | **21.45** | $[15.95, \; 27.10]$ | 0.0% | **Two Lost Decades**: Complete stagnation at 2024 capability baseline. |
| **Resilient 4D+ Response** | **56.40** | $[52.30, \; 59.80]$ | **99.5%** | **Industrial Takeoff**: Neutralizes external shocks; matches Vietnam today. |

---

## 📊 Key Publication Figures

All figures are generated at 300 DPI in `outputs/figures/`:

| Figure | Description |
| :--- | :--- |
| **[Figure 1](outputs/figures/fig1_demographic_dividend.png)** | Demographic Dividend Window: Japan (1950–1990) vs. Bangladesh (1990–2046) |
| **[Figure 2](outputs/figures/fig2_economic_complexity_chasm.png)** | Economic Complexity Chasm & Product Space Diversification |
| **[Figure 3](outputs/figures/fig3_bangladesh_2045_fan_charts.png)** | 20-Year Fan Charts (Monte Carlo Paths) across 5 Scenarios (2026–2046) |
| **[Figure 4](outputs/figures/fig4_capability_radar.png)** | 9D Capability Radar: Japan vs. Bangladesh 2026 vs. Bangladesh 2046 |
| **[Figure 5](outputs/figures/fig5_macro_monetary_projections.png)** | Macro Monetary & Dollar Projections: PPP GDP, Tax Net & Export Dividend (2026–2046) |

---

## 🎮 Interactive Web Dashboards & Simulators

We provide three interactive platforms to explore the policy parameter space:

1. **Live Web Browser Dashboard (GitHub Pages)**:
   - 🌐 **Instant Access**: [**https://rbr48.github.io/4d-epdm/**](https://rbr48.github.io/4d-epdm/)
   - Fully interactive, client-side simulation running directly in any modern browser on mobile or desktop without installation. Real-time parameter tweaking and 9D capability radar updates.

2. **Streamlit Local Application**:
   ```bash
   pip install streamlit
   streamlit run dashboard.py
   # Or:
   make dashboard
   ```
   Full-featured local Streamlit sandbox with interactive sliders for tax mobilization, deep-sea port logistics, product complexity, vocational skills, and toggleable adversarial shocks.

3. **Zero-Dependency Standalone HTML File**:
   - Double-click [`index.html`](index.html) or [`outputs/interactive_dashboard.html`](outputs/interactive_dashboard.html) locally to run offline in any web browser.

---

## 🏛️ Strategic 4-Pillar Roadmap for Bangladesh

To replicate Japan's postwar trajectory and avoid the middle-income trap, Bangladesh must execute an integrated four-pillar transformation with feasible political-economy sequencing:

1. **8.1 Domestic Fiscal Mobilization & Banking Resolution**:
   - Raise tax-to-GDP from ~7.6% to 15–16% via end-to-end digital automation (EFDs, digitized customs) to minimize discretionary corruption.
   - Establish an autonomous National Asset Management Company (AMC) and dedicated commercial bankruptcy courts to resolve banking non-performing loans (NPLs).
2. **8.2 Maritime Trade Logistics & Port Gravity**:
   - Accelerate Matarbari deep-sea port and regional connectivity corridors, establishing Bangladesh as the Bay of Bengal transshipment hub.
3. **8.3 Product Space Leap & Economic Complexity**:
   - Diversify beyond ready-made garments into Active Pharmaceutical Ingredients (APIs), electronics/PCB assembly, light engineering, and shipbuilding.
   - Enforce Alice Amsden's *reciprocal control mechanisms*: time-bound, export-contingent subsidies rather than permanent entitlements.
4. **8.4 Vocational Human Capital & Institutional Meritocracy**:
   - Reorient tertiary education toward German/Japanese dual vocational training and technical engineering certifications.

---

## 🚀 Quickstart & Replication

### Installation & Environment
```bash
git clone https://github.com/rbr48/4d-epdm.git
cd 4d-epdm

# Via pip requirements lockfile:
pip install -r requirements.txt

# Or via Conda:
conda env create -f environment.yml
conda activate 4d-epdm
```

### 1-Click Master Reproduction
Reproduce the entire empirical paper, 19-origin evaluations, 20-year Monte Carlo trajectories, stress-testing suite, and publication figures in a single command:
```bash
python run_all.py --all
# Or via GNU Make:
make reproduce-paper
```

### Modular Execution
```bash
python run_evaluation.py          # Out-of-sample rolling-origin evaluation (make eval)
python power_dynamics_engine.py    # 9D capability simulation & Monte Carlo (make sim)
python stress_testing.py           # Crisis split, archetype & placebo tests (make stress)
python generate_video_figures.py   # Publication 300 DPI figures (make figures)
streamlit run dashboard.py         # Launch Streamlit web dashboard (make dashboard)
```

---

## 📁 Repository Structure

```
4d-epdm/
├── PRE_REGISTRATION.md                         # Pre-registered hypotheses and benchmarking protocol
├── RESEARCH_PAPER_AND_DISSERTATION_CHAPTER.md  # Complete academic working paper & dissertation chapter
├── README.md                                   # Comprehensive repository documentation
├── Makefile                                    # Automation targets for GNU Make
├── requirements.txt                            # Pinned Python package dependencies
├── environment.yml                             # Conda environment definition
├── run_all.py                                  # 1-Click master replication pipeline CLI
├── candidate_model.py                          # Engine 1: NCD-LP direct local projection forecaster
├── power_dynamics_engine.py                    # Engine 2: 9D capability state space & 20-yr Monte Carlo
├── run_evaluation.py                           # 19 rolling origins zero-leakage evaluation harness
├── stress_testing.py                           # Crisis split, archetype heterogeneity, placebo permutation
├── generate_video_figures.py                   # 300 DPI visualization generation script
├── dashboard.py                                # Streamlit interactive capability sandbox
├── data_layer.py                               # Macroeconomic data ingestion & panel construction
├── evaluation.py                               # Benchmark estimators & Diebold-Mariano tests
├── outputs/                                    # Evaluation logs, weight checks, and figures
│   ├── figures/                                # Publication-ready figures (PNG, 300 DPI)
│   ├── interactive_dashboard.html              # Standalone zero-dependency browser visualizer
│   └── weight_robustness_check.csv             # Weight schema robustness audit
└── data/                                       # Raw World Bank WDI and PWT empirical datasets
```

---

## 📜 Citation & Academic Working Paper

If you use this model or code in your research, please cite:

```bibtex
@techreport{izhaan2026_4depdm,
  title={Japan’s Rise as an Economic Superpower and a Validated Dual-Engine Development Architecture for Bangladesh},
  author={Izhaan Intellect Research Series},
  year={2026},
  month={September},
  institution={Izhaan Intellect},
  type={Working Paper and Dissertation Chapter},
  url={https://github.com/rbr48/4d-epdm}
}
```

---

## 📄 License
This research project is licensed under the [MIT License](LICENSE).
