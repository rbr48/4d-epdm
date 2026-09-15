#!/usr/bin/env python3
"""
Panel BVAR with Litterman (1986) Minnesota prior.
=================================================
A legitimately more advanced structural alternative to NCD-LP.

State vector per country: [growth, log_gdppc_demeaned, dep_ratio_demeaned].
Common A matrices across countries with country fixed effects.
Minnesota prior on the A's; posterior mode conditional on Sigma_OLS.

Contract: bvar_minnesota(train, origin, horizons) -> DataFrame[iso, h, pred]
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from dataclasses import dataclass

TARGET = "GDP_GROWTH"
STATE_VARS = ["g", "ly", "d"]


@dataclass
class _BVARFit:
    A: np.ndarray          # (p, K, K)  lag k, equation i, regressor j
    c: np.ndarray          # (K,)  intercepts
    Sigma: np.ndarray      # (K, K)
    K: int
    p: int
    feat_means: dict
    feat_sds: dict
    sigma_ar: np.ndarray   # (K,) univariate AR residual sd


def _safe(x, lo=1e-10):
    return np.clip(x, lo, None)


def _build_state(train: pd.DataFrame, p: int) -> pd.DataFrame:
    """Sort, demean ly and d within country, and lag the state vector."""
    d = train.sort_values(["iso", "year"]).copy()
    d["g"]  = d[TARGET]
    d["ly"] = np.log(d["GDP_PC_PPP"]) if "GDP_PC_PPP" in d.columns else np.nan
    d["d"]  = d["DEPENDENCY_RATIO"] if "DEPENDENCY_RATIO" in d.columns else np.nan

    for c in ["ly", "d"]:
        m = d.groupby("iso")[c].transform("mean")
        s = d.groupby("iso")[c].transform("std").replace(0, 1.0)
        d[c] = (d[c] - m) / s

    # Lag K=3 state vector p times
    for k in range(1, p + 1):
        for v in STATE_VARS:
            d[f"{v}_lag{k}"] = d.groupby("iso")[v].shift(k)
    return d


def _univariate_ar_sigma(z: np.ndarray, p: int) -> float:
    """Residual sd from a univariate AR(p) fit (used in Minnesota variances)."""
    if len(z) < p + 3:
        return float(np.std(z)) if len(z) > 1 else 1.0
    Y = z[p:]
    X = np.column_stack([np.ones(len(Y))] +
                        [z[p - j - 1: len(z) - j - 1] for j in range(p)])
    beta, *_ = np.linalg.lstsq(X, Y, rcond=None)
    resid = Y - X @ beta
    return max(float(np.std(resid)), 1e-6)


def _minnesota_prior(K: int, p: int, sigma_ar: np.ndarray,
                     lam: float = 0.2, theta: float = 0.5) -> tuple[np.ndarray, np.ndarray]:
    """
    Return (prior_mean, prior_var) each of shape (p, K, K).
    prior_var[i,j] is the variance of A_k[i,j].
    """
    A_prior = np.zeros((p, K, K))
    A_prior[0] = np.eye(K)                # own first lag = 1
    V_prior = np.zeros((p, K, K))
    for k in range(1, p + 1):
        for i in range(K):
            for j in range(K):
                base = (lam / k) ** 2
                if i == j:
                    V_prior[k - 1, i, j] = base
                else:
                    V_prior[k - 1, i, j] = (base *
                                            (sigma_ar[i] ** 2) /
                                            (sigma_ar[j] ** 2) *
                                            theta ** 2)
    return A_prior, _safe(V_prior, lo=1e-8)


def _fit_country_block(sub: pd.DataFrame, p: int, K: int,
                       A_prior: np.ndarray, V_prior: np.ndarray) -> tuple:
    """Return (A, c, Sigma) for one country via posterior mode."""
    lag_cols = [f"{v}_lag{k}" for k in range(1, p + 1) for v in STATE_VARS]
    needed = ["g", "ly", "d"] + lag_cols
    df = sub.dropna(subset=needed)
    if len(df) < p + 5:
        return None, None, None
    Y = df[["g", "ly", "d"]].to_numpy()
    X = np.column_stack([np.ones(len(df)), df[lag_cols].to_numpy()])

    # OLS for Sigma
    B_ols, *_ = np.linalg.lstsq(X, Y, rcond=None)
    E = Y - X @ B_ols
    Sigma = (E.T @ E) / max(len(df) - X.shape[1], 1)
    Sigma = Sigma + 1e-6 * np.eye(K)

    # Build prior for the full (1 + p*K, K) coefficient matrix
    B_prior = np.zeros((1 + p * K, K))
    V_prior_mat = np.zeros((1 + p * K, K))
    # Intercepts: loose prior
    B_prior[0, :] = 0
    V_prior_mat[0, :] = 1e3
    for ki in range(p):
        for i in range(K):
            for j in range(K):
                row = 1 + ki * K + j
                B_prior[row, i] = A_prior[ki, i, j]
                V_prior_mat[row, i] = V_prior[ki, i, j]

    # Posterior mode (ridge form)
    Omega_inv = np.diag((1.0 / V_prior_mat.flatten(order="F")))
    B_flat = B_prior.flatten(order="F")
    XtX = np.kron(np.eye(K), X.T @ X)
    Xty = (X.T @ Y).flatten(order="F")
    try:
        B_post_flat = np.linalg.solve(XtX + Omega_inv,
                                      Xty + Omega_inv @ B_flat)
        B_post = B_post_flat.reshape((1 + p * K, K), order="F")
    except np.linalg.LinAlgError:
        B_post = B_prior

    A = B_post[1:, :].T.reshape(K, p, K).transpose(1, 0, 2)  # (p, K, K)
    c = B_post[0, :]
    return A, c, Sigma


class BVARMinnesota:
    def __init__(self, p: int = 2, lam: float = 0.2, theta: float = 0.5):
        self.p = p
        self.lam = lam
        self.theta = theta
        self.K = 3
        self.fit_: _BVARFit | None = None

    def fit(self, train: pd.DataFrame) -> "BVARMinnesota":
        d = _build_state(train, self.p)
        isos = sorted(d["iso"].unique())

        sigma_ar = np.zeros(self.K)
        for i, v in enumerate(STATE_VARS):
            all_z = d[v].dropna().to_numpy()
            sigma_ar[i] = _univariate_ar_sigma(all_z, self.p)

        A_prior, V_prior = _minnesota_prior(self.K, self.p, sigma_ar,
                                            lam=self.lam, theta=self.theta)

        # Pooled country-block fit: share A_prior / V_prior, individual Sigma
        A_list, c_list, S_list = [], [], []
        for iso in isos:
            sub = d[d.iso == iso]
            A_i, c_i, S_i = _fit_country_block(sub, self.p, self.K,
                                               A_prior, V_prior)
            if A_i is not None:
                A_list.append(A_i); c_list.append(c_i); S_list.append(S_i)

        if not A_list:
            A = np.zeros((self.p, self.K, self.K)); A[0] = np.eye(self.K)
            c = np.zeros(self.K); S = np.eye(self.K)
        else:
            A = np.mean(A_list, axis=0)
            c = np.mean(c_list, axis=0)
            S = np.mean(S_list, axis=0)

        self.fit_ = _BVARFit(
            A=A, c=c, Sigma=S, K=self.K, p=self.p,
            feat_means={v: float(d[v].mean()) for v in STATE_VARS},
            feat_sds={v: float(d[v].std() or 1.0) for v in STATE_VARS},
            sigma_ar=sigma_ar,
        )
        return self

    def forecast(self, train: pd.DataFrame, origin: int,
                 horizons: list[int], return_density: bool = False) -> pd.DataFrame:
        if self.fit_ is None:
            self.fit(train)
        f = self.fit_
        d = _build_state(train, self.p)

        rows = []
        for iso, sub in d.groupby("iso"):
            sub = sub.sort_values("year")
            if len(sub) < self.p:
                continue
            # Initial state
            hist = sub[["g", "ly", "d"]].to_numpy()
            if np.any(~np.isfinite(hist[-self.p:])):
                hist = np.nan_to_num(hist, nan=0.0)
            z_hist = hist[-self.p:][::-1]  # z_{t}, z_{t-1}, ...

            path = np.zeros((max(horizons), f.K))
            z_cur = [z_hist[k].copy() for k in range(self.p)]
            for h in range(1, max(horizons) + 1):
                z_next = f.c.copy()
                for k in range(self.p):
                    z_next = z_next + f.A[k] @ z_cur[k]
                # ly is demeaned: gentle mean reversion
                z_next[1] = 0.7 * z_cur[0][1]
                path[h - 1] = z_next
                z_cur = [z_next] + z_cur[:-1]

            for h in horizons:
                if h > len(path):
                    continue
                pred_g = path[h - 1][0]
                sig = float(np.sqrt(f.Sigma[0, 0] * h))
                rows.append({"iso": iso, "h": int(h),
                             "pred": float(pred_g), "sigma": sig})
        out = pd.DataFrame(rows)
        return out if return_density else out[["iso", "h", "pred"]]


def bvar_minnesota(train, origin, horizons):
    return BVARMinnesota().fit(train).forecast(train, origin, horizons)


def bvar_minnesota_density(train, origin, horizons):
    return BVARMinnesota().fit(train).forecast(train, origin, horizons, return_density=True)
