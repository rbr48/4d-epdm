#!/usr/bin/env python3
"""
Bayesian Model Averaging over density forecasts.
================================================
Weights from rolling held-out predictive likelihood.
No grid search. No validation-set tuning. No "best model" selection.

Inputs : a list of (name, density_forecaster) where density_forecaster
         follows the contract:
             f(train, origin, horizons) -> DataFrame[iso, h, pred, sigma]
Output : DataFrame[iso, h, pred, sigma] using BMA mixture density,
         plus a per-origin weight table saved for audit.

Contract: bma_forecaster(train, origin, horizons) -> DataFrame[iso, h, pred]
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from pathlib import Path
from scipy import stats
from dataclasses import dataclass

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)
TARGET = "GDP_GROWTH"


# ---------- helpers ----------

def _logpdf(y: np.ndarray, mu: np.ndarray, sigma: np.ndarray) -> np.ndarray:
    sigma = np.clip(sigma, 1e-6, None)
    return -0.5 * np.log(2 * np.pi) - np.log(sigma) - 0.5 * ((y - mu) / sigma) ** 2


@dataclass
class _BMAResult:
    weights: dict[str, float]
    mu: float
    sigma: float


class BMAForecaster:
    """
    Fit: score each candidate on the last `holdout_years` of train using
    rolling predictive likelihood. Weight ∝ exp(sum logpdf).

    Forecast: combine density forecasts by mixture.
    """

    def __init__(self,
                 candidates: list[tuple[str, callable]],
                 holdout_years: int = 8,
                 min_holdout_origins: int = 4,
                 prior_weights: dict[str, float] | None = None,
                 temperature: float = 1.0):
        self.candidates = candidates
        self.holdout_years = holdout_years
        self.min_holdout_origins = min_holdout_origins
        self.prior_weights = prior_weights or {n: 1.0 for n, _ in candidates}
        self.temperature = temperature
        self.weights_: dict[str, float] = {}

    # ---------- weight estimation ----------

    def _holdout_origins(self, train: pd.DataFrame, horizons: list[int]) -> list[int]:
        years = np.sort(train["year"].unique())
        maxh = max(horizons)
        last_valid = int(years[-1]) - maxh
        first_valid = int(years[0]) + 12
        origins = [y for y in range(last_valid - self.holdout_years + 1,
                                    last_valid + 1)
                   if y >= first_valid]
        return origins

    def _score_candidate(self, name: str, fn: callable,
                         train: pd.DataFrame, horizons: list[int]) -> float:
        """Sum of log predictive density on holdout origins."""
        origins = self._holdout_origins(train, horizons)
        if len(origins) < self.min_holdout_origins:
            return 0.0
        total = 0.0
        n = 0
        for o in origins:
            sub = train[train.year <= o]
            fut = train[(train.year > o) & (train.year <= o + max(horizons))]
            if fut.empty:
                continue
            try:
                pred = fn(sub, o, horizons)
            except Exception:
                continue
            actual = {(r.iso, int(r.year - o)): r.GDP_GROWTH
                      for r in fut.itertuples() if pd.notna(r.GDP_GROWTH)}
            for p in pred.itertuples():
                key = (p.iso, int(p.h))
                if key not in actual:
                    continue
                sigma = getattr(p, "sigma", None)
                if sigma is None or not np.isfinite(sigma) or sigma <= 0:
                    sigma = 1.0
                total += float(_logpdf(np.array([actual[key]]),
                                       np.array([p.pred]),
                                       np.array([sigma]))[0])
                n += 1
        return total / max(n, 1)

    def fit_weights(self, train: pd.DataFrame, horizons: list[int]) -> dict[str, float]:
        raw = {}
        for name, fn in self.candidates:
            raw[name] = self._score_candidate(name, fn, train, horizons)
        # Temperature scaling + prior
        logits = np.array([raw[n] * self.temperature + np.log(self.prior_weights[n])
                           for n, _ in self.candidates])
        logits -= logits.max()
        w = np.exp(logits); w /= w.sum()
        self.weights_ = {n: float(wi) for (n, _), wi in zip(self.candidates, w)}
        return self.weights_

    def forecast(self, train: pd.DataFrame, origin: int,
                 horizons: list[int], return_density: bool = True) -> pd.DataFrame:
        if not getattr(self, "_has_fitted", False):
            origins = self._holdout_origins(train, horizons)
            if len(origins) >= self.min_holdout_origins:
                self.fit_weights(train, horizons)
                self._has_fitted = True
            elif not self.weights_:
                self.weights_ = {n: 1.0 / len(self.candidates) for n, _ in self.candidates}

        # Collect (iso, h, mu, sigma) from each candidate
        per_model: dict[str, pd.DataFrame] = {}
        for name, fn in self.candidates:
            try:
                df = fn(train, origin, horizons)
            except Exception:
                continue
            if "sigma" not in df.columns:
                df = df.assign(sigma=1.0)
            per_model[name] = df.set_index(["iso", "h"]).sort_index()

        if not per_model:
            return pd.DataFrame(columns=["iso", "h", "pred", "sigma"])

        # Union of keys (should be identical, but be safe)
        all_keys = sorted(set().union(*[set(df.index) for df in per_model.values()]))

        rows = []
        # Precompute weight vector in candidate order (fill in missing = 0)
        active = [n for n in self.weights_ if n in per_model]
        if not active:
            return pd.DataFrame(columns=["iso", "h", "pred", "sigma"])
        w = np.array([self.weights_[n] for n in active])
        w /= w.sum()

        for key in all_keys:
            mus, sigs, ws = [], [], []
            for n, wi in zip(active, w):
                df = per_model[n]
                if key in df.index:
                    row = df.loc[key]
                    mus.append(float(row["pred"]))
                    sigs.append(max(float(row.get("sigma", 1.0)), 1e-6))
                    ws.append(wi)
            if not mus:
                continue
            ww = np.array(ws); ww /= ww.sum()
            mu = float(np.sum(ww * np.array(mus)))
            # Mixture variance
            var = float(np.sum(ww * (np.array(sigs) ** 2 + np.array(mus) ** 2)) - mu ** 2)
            sigma = float(np.sqrt(max(var, 1e-6)))
            rows.append({"iso": key[0], "h": int(key[1]),
                         "pred": mu, "sigma": sigma})

        out = pd.DataFrame(rows)
        return out if return_density else out[["iso", "h", "pred"]]

    def save_weights(self, path: Path = OUT / "bma_weights.csv"):
        pd.DataFrame([{"model": k, "weight": v}
                      for k, v in self.weights_.items()]).to_csv(path, index=False)


# ---------- entry points matching evaluation.py contract ----------

def _build_default():
    from advanced_model import hb_dlp_sv_density
    from bvar_minnesota import bvar_minnesota_density
    from gbrt_model import gbrt_density
    return BMAForecaster(candidates=[
        ("HB-DLP-SV", hb_dlp_sv_density),
        ("BVAR-MN",   bvar_minnesota_density),
        ("GBRT",      gbrt_density),
    ])


_BMA_SINGLETON = None

def bma_forecaster(train, origin, horizons):
    global _BMA_SINGLETON
    if _BMA_SINGLETON is None:
        _BMA_SINGLETON = _build_default()
    return _BMA_SINGLETON.forecast(train, origin, horizons, return_density=False)


def bma_density(train, origin, horizons):
    global _BMA_SINGLETON
    if _BMA_SINGLETON is None:
        _BMA_SINGLETON = _build_default()
    return _BMA_SINGLETON.forecast(train, origin, horizons, return_density=True)
