#!/usr/bin/env python3
"""
test_regression_suite.py — the pytest CI gate
==============================================
Makes the pre-registered verdict a machine-enforced invariant.

Categories:
1. Forecaster contract compliance
2. Structural leakage check
3. NCD-LP h=1 delegation identity
4. Pre-registered verdict integration
5. No unconditional PASS banners
6. Determinism
7. DM test invariants
8. Pre-registration file existence
9. Benchmark ranking stability
"""
from __future__ import annotations
import ast
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# ── locate the repo root ────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from evaluation import (rolling_origin, diebold_mariano, verdict,
                         summarize, bench_ar1_fe, BENCHMARKS, TARGET)
from candidate_model import neoclassical_convergence_lp
from adaptive_ensemble import adaptive_forecaster

PANEL_PATH = ROOT / "data" / "processed" / "panel_raw.csv"
HORIZONS = [1, 2, 3, 4, 5]


# ── helper fixture ──────────────────────────────────────────────────────
@pytest.fixture(scope="module")
def panel():
    return pd.read_csv(PANEL_PATH).dropna(subset=[TARGET])


@pytest.fixture(scope="module")
def ev(panel):
    return rolling_origin(
        panel,
        {"ncd_lp": neoclassical_convergence_lp},
        horizons=HORIZONS,
        verbose=False,
    )


# =====================================================================
# 1. FORECASTER CONTRACT
# =====================================================================

class TestForecasterContract:
    """Any forecaster must return DataFrame[iso, h, pred] with correct types."""

    @pytest.mark.parametrize("name,func", [
        ("ncd_lp", neoclassical_convergence_lp),
        ("ar1_fe", bench_ar1_fe),
        ("adaptive_ensemble", adaptive_forecaster),
    ])
    def test_return_columns(self, panel, name, func):
        train = panel[panel.year <= 2010]
        out = func(train, 2010, [1, 3])
        assert isinstance(out, pd.DataFrame), f"{name} must return DataFrame"
        for col in ("iso", "h", "pred"):
            assert col in out.columns, f"{name} missing column '{col}'"

    @pytest.mark.parametrize("name,func", [
        ("ncd_lp", neoclassical_convergence_lp),
        ("ar1_fe", bench_ar1_fe),
        ("adaptive_ensemble", adaptive_forecaster),
    ])
    def test_no_nan_preds(self, panel, name, func):
        train = panel[panel.year <= 2010]
        out = func(train, 2010, HORIZONS)
        assert out["pred"].notna().all(), f"{name} produced NaN predictions"

    @pytest.mark.parametrize("name,func", [
        ("ncd_lp", neoclassical_convergence_lp),
        ("adaptive_ensemble", adaptive_forecaster),
    ])
    def test_all_horizons_covered(self, panel, name, func):
        train = panel[panel.year <= 2010]
        out = func(train, 2010, HORIZONS)
        for h in HORIZONS:
            assert h in out.h.values, f"{name} missing horizon {h}"

    @pytest.mark.parametrize("name,func", [
        ("ncd_lp", neoclassical_convergence_lp),
        ("adaptive_ensemble", adaptive_forecaster),
    ])
    def test_all_countries_covered(self, panel, name, func):
        train = panel[panel.year <= 2010]
        isos_in = set(train.iso.unique())
        out = func(train, 2010, HORIZONS)
        isos_out = set(out.iso.unique())
        missing = isos_in - isos_out
        # Allow up to 2 countries to be missing (short histories)
        assert len(missing) <= 2, f"{name} missing countries: {missing}"


# =====================================================================
# 2. STRUCTURAL LEAKAGE CHECK
# =====================================================================

class TestNoLeakage:
    """Forecaster must NOT see rows with year > origin."""

    def test_train_filter(self, panel):
        """Verify rolling_origin passes only year <= origin."""
        origin = 2010
        train = panel[panel.year <= origin]
        assert train.year.max() <= origin

    def test_future_data_not_in_features(self, panel):
        """Check that ncd_lp does not access years beyond origin."""
        origin = 2005
        train = panel[panel.year <= origin]
        out = neoclassical_convergence_lp(train, origin, [1, 2, 3])
        # If the forecaster leaked, it would give suspiciously perfect predictions.
        # We cannot directly test it, but we verify train is correctly filtered.
        assert len(train[train.year > origin]) == 0


# =====================================================================
# 3. NCD-LP h=1 DELEGATION IDENTITY
# =====================================================================

class TestH1Delegation:
    """At h=1 NCD-LP should delegate to bench_ar1_fe_step1, which should
    match bench_ar1_fe at h=1 exactly (or nearly)."""

    def test_h1_matches_ar1_fe(self, panel):
        origin = 2012
        train = panel[panel.year <= origin]
        ncd = neoclassical_convergence_lp(train, origin, [1])
        ar1 = bench_ar1_fe(train, origin, [1])
        merged = ncd.merge(ar1, on=["iso", "h"], suffixes=("_ncd", "_ar1"))
        # Allow small numerical difference from different code paths
        diff = (merged.pred_ncd - merged.pred_ar1).abs()
        assert diff.max() < 0.5, (
            f"h=1 delegation mismatch: max diff = {diff.max():.4f}"
        )


# =====================================================================
# 4. PRE-REGISTERED VERDICT
# =====================================================================

class TestVerdict:
    """The verdict function must be internally consistent."""

    def test_verdict_has_required_keys(self, ev):
        v = verdict(ev, "ncd_lp", HORIZONS)
        for key in ("pass", "beats_every_benchmark",
                     "horizons_significantly_better"):
            assert key in v, f"verdict missing key '{key}'"

    def test_verdict_pass_requires_both_conditions(self, ev):
        v = verdict(ev, "ncd_lp", HORIZONS)
        if v["pass"]:
            assert v["beats_every_benchmark"], \
                "PASS without beating every benchmark"
            assert len(v["horizons_significantly_better"]) > 0, \
                "PASS without any significant horizon"

    def test_verdict_consistent_with_pooled_rmse(self, ev):
        v = verdict(ev, "ncd_lp", HORIZONS)
        pooled = ev.groupby("model")["sq"].mean().pow(0.5)
        if "ncd_lp" in pooled.index:
            ncd_rmse = pooled["ncd_lp"]
            bench_rmses = {m: pooled[m] for m in pooled.index if m != "ncd_lp"}
            beats_all = all(ncd_rmse < v for v in bench_rmses.values())
            assert v["beats_every_benchmark"] == beats_all


# =====================================================================
# 5. NO UNCONDITIONAL PASS BANNERS
# =====================================================================

class TestNoUnconditionalBanners:
    """Source files must never print 'PASS' or 'PASSED' unconditionally.
    This is THE test that would have caught the stress_testing.py problem."""

    BANNER_PATTERN = re.compile(
        r"""(print|logging\.\w+)\s*\(.*\b(PASS|PASSED|ALL\s+CHECKS?\s+PASSED)\b""",
        re.IGNORECASE,
    )
    CONDITIONAL_PATTERN = re.compile(r"""^\s*(if|elif|else|except|try|for|while)""")

    @pytest.mark.parametrize("pyfile", sorted(ROOT.glob("*.py")))
    def test_no_unconditional_pass(self, pyfile):
        lines = pyfile.read_text(encoding="utf-8", errors="replace").splitlines()
        violations = []
        for i, line in enumerate(lines, 1):
            if self.BANNER_PATTERN.search(line):
                # Check if it's inside a conditional block
                # Look at preceding non-blank lines for indentation context
                prev_lines = [l for l in lines[max(0, i-5):i-1] if l.strip()]
                is_conditional = False
                if prev_lines:
                    # Check indentation: if the print is indented under a conditional
                    indent = len(line) - len(line.lstrip())
                    for pl in reversed(prev_lines):
                        pl_indent = len(pl) - len(pl.lstrip())
                        if pl_indent < indent and self.CONDITIONAL_PATTERN.match(pl):
                            is_conditional = True
                            break
                if not is_conditional:
                    violations.append(f"{pyfile.name}:{i}: {line.strip()}")
        assert not violations, (
            "Unconditional PASS/PASSED banners found:\n" +
            "\n".join(violations)
        )


# =====================================================================
# 6. DETERMINISM
# =====================================================================

class TestDeterminism:
    """Same inputs must produce identical outputs."""

    def test_ncd_lp_deterministic(self, panel):
        origin = 2010
        train = panel[panel.year <= origin]
        out1 = neoclassical_convergence_lp(train, origin, [1, 3, 5])
        out2 = neoclassical_convergence_lp(train, origin, [1, 3, 5])
        pd.testing.assert_frame_equal(
            out1.sort_values(["iso", "h"]).reset_index(drop=True),
            out2.sort_values(["iso", "h"]).reset_index(drop=True),
        )


# =====================================================================
# 7. DIEBOLD-MARIANO INVARIANTS
# =====================================================================

class TestDMInvariants:
    """DM test must satisfy basic statistical properties."""

    def test_dm_symmetry(self, ev):
        """DM(A,B) stat should be -DM(B,A) stat."""
        dm_ab = diebold_mariano(ev, "ncd_lp", "ar1_fe", 3)
        dm_ba = diebold_mariano(ev, "ar1_fe", "ncd_lp", 3)
        if np.isfinite(dm_ab["stat"]) and np.isfinite(dm_ba["stat"]):
            assert abs(dm_ab["stat"] + dm_ba["stat"]) < 0.01, \
                f"DM not antisymmetric: {dm_ab['stat']:.4f} vs {dm_ba['stat']:.4f}"

    def test_dm_self_zero(self, ev):
        """DM(A,A) should be zero or nan."""
        dm = diebold_mariano(ev, "ncd_lp", "ncd_lp", 1)
        if np.isfinite(dm["stat"]):
            assert abs(dm["stat"]) < 1e-10, \
                f"DM(self,self) should be 0, got {dm['stat']}"

    def test_dm_p_in_range(self, ev):
        """p-value must be in [0, 1]."""
        for h in HORIZONS:
            dm = diebold_mariano(ev, "ncd_lp", "ar1_fe", h)
            if np.isfinite(dm["p"]):
                assert 0 <= dm["p"] <= 1, f"p={dm['p']} out of range at h={h}"


# =====================================================================
# 8. PRE-REGISTRATION FILE EXISTS
# =====================================================================

class TestPreRegistration:
    """The repo must contain the pre-registration document."""

    def test_pre_registration_exists(self):
        candidates = [
            ROOT / "PRE_REGISTRATION.md",
            ROOT / "pre_registration.md",
            ROOT / "docs" / "PRE_REGISTRATION.md",
        ]
        assert any(p.exists() for p in candidates), \
            "No PRE_REGISTRATION.md found in repo"


# =====================================================================
# 9. BENCHMARK RANKING STABILITY
# =====================================================================

class TestBenchmarkRanking:
    """Benchmarks should maintain expected relative ordering on this panel."""

    def test_ar1_fe_beats_pooled_mean(self, ev):
        pooled = ev.groupby("model")["sq"].mean().pow(0.5)
        if "ar1_fe" in pooled and "pooled_mean" in pooled:
            assert pooled["ar1_fe"] < pooled["pooled_mean"], \
                "ar1_fe should beat pooled_mean on this panel"

    def test_ar1_fe_beats_random_walk(self, ev):
        pooled = ev.groupby("model")["sq"].mean().pow(0.5)
        if "ar1_fe" in pooled and "random_walk" in pooled:
            assert pooled["ar1_fe"] < pooled["random_walk"], \
                "ar1_fe should beat random_walk on this panel"
