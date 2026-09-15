#!/usr/bin/env python3
"""
GBRT falsification tool.
========================
Gradient-Boosted Regression Trees as a ceiling test.

Most likely finding: GBRT will overfit the panel on this sample size
(16 countries x ~35 years = 560 rows) and produce pooled RMSE equal to
or worse than ar1_fe. That result is a FEATURE: it shows nonlinearities
don't help, which is honest and important.

Contract: gbrt_forecaster(train, origin, horizons) -> DataFrame[iso, h, pred]
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import TimeSeriesSplit

TARGET = "GDP_GROWTH"


def _build_features(train: pd.DataFrame) -> pd.DataFrame:
    """Construct ML-ready features from the panel."""
    d = train.sort_values(["iso", "year"]).copy()
    d["ly"] = np.log(d["GDP_PC_PPP"]).replace([np.inf, -np.inf], np.nan)
    d["dr"] = d["DEPENDENCY_RATIO"]
    d["y_lag1"] = d.groupby("iso")[TARGET].shift(1)
    d["y_lag2"] = d.groupby("iso")[TARGET].shift(2)
    d["y_lag3"] = d.groupby("iso")[TARGET].shift(3)
    d["ly_lag1"] = d.groupby("iso")["ly"].shift(1)
    d["dr_lag1"] = d.groupby("iso")["dr"].shift(1)
    d["y_ma3"] = d.groupby("iso")[TARGET].transform(
        lambda x: x.shift(1).rolling(3, min_periods=1).mean())
    return d


FEAT_COLS = ["y_lag1", "y_lag2", "y_lag3", "ly_lag1", "dr_lag1", "y_ma3"]


def _fit_gbrt(d: pd.DataFrame, h: int, max_depth: int = 3,
              n_estimators: int = 200, lr: float = 0.05,
              subsample: float = 0.8) -> GradientBoostingRegressor:
    """
    Fit GBR for horizon h with time-series–aware cross-validation for
    early stopping.
    """
    y_col = f"y_lead{h}"
    d = d.copy()
    d[y_col] = d.groupby("iso")[TARGET].shift(-h)
    df = d.dropna(subset=FEAT_COLS + [y_col])
    if len(df) < 30:
        return None
    X = df[FEAT_COLS].to_numpy()
    y = df[y_col].to_numpy()

    tscv = TimeSeriesSplit(n_splits=3)
    best_n, best_val = n_estimators, np.inf
    for train_idx, val_idx in tscv.split(X):
        m = GradientBoostingRegressor(
            n_estimators=n_estimators, max_depth=max_depth,
            learning_rate=lr, subsample=subsample,
            random_state=42)
        m.fit(X[train_idx], y[train_idx])
        staged = list(m.staged_predict(X[val_idx]))
        for n_est, pred in enumerate(staged, 1):
            mse = float(np.mean((pred - y[val_idx]) ** 2))
            if mse < best_val:
                best_val = mse
                best_n = n_est

    final = GradientBoostingRegressor(
        n_estimators=best_n, max_depth=max_depth,
        learning_rate=lr, subsample=subsample,
        random_state=42)
    final.fit(X, y)
    residuals = y - final.predict(X)
    sigma = float(np.std(residuals)) if len(residuals) > 1 else 1.0
    return final, max(sigma, 0.5)


def gbrt_forecaster(train: pd.DataFrame, origin: int,
                    horizons: list[int]) -> pd.DataFrame:
    """GBRT forecaster conforming to evaluation.py contract."""
    d = _build_features(train)
    rows = []
    for h in horizons:
        res = _fit_gbrt(d, h)
        if res[0] is None:
            continue
        model, _ = res
        for iso, sub in d.groupby("iso"):
            sub = sub.sort_values("year")
            last = sub.iloc[-1:]
            feats = last[FEAT_COLS]
            if feats.isna().any(axis=1).any():
                pred_val = float(sub[TARGET].iloc[-1])
            else:
                pred_val = float(model.predict(feats.to_numpy())[0])
            rows.append({"iso": iso, "h": int(h), "pred": pred_val})
    return pd.DataFrame(rows)


def gbrt_density(train: pd.DataFrame, origin: int,
                 horizons: list[int]) -> pd.DataFrame:
    """GBRT density forecaster returning mu (pred) and sigma."""
    d = _build_features(train)
    rows = []
    for h in horizons:
        res = _fit_gbrt(d, h)
        if res[0] is None:
            continue
        model, sigma = res
        for iso, sub in d.groupby("iso"):
            sub = sub.sort_values("year")
            last = sub.iloc[-1:]
            feats = last[FEAT_COLS]
            if feats.isna().any(axis=1).any():
                pred_val = float(sub[TARGET].iloc[-1])
            else:
                pred_val = float(model.predict(feats.to_numpy())[0])
            rows.append({"iso": iso, "h": int(h), "pred": pred_val, "sigma": sigma})
    return pd.DataFrame(rows)

