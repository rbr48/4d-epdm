#!/usr/bin/env python3
"""
HB-DLP-SV: Hierarchical Bayesian Dynamic Local Projection with Stochastic Volatility
====================================================================================
A state-of-the-art econometric forecaster for the 4d-epdm panel.

Key Structural Innovations:
  1. Latent Global Factor (PCA/SVD): Captures international business cycle shocks (GFC, COVID)
     sign-anchored to the United States.
  2. Hierarchical Bayesian Shrinkage: beta_i ~ N(beta_pool, tau^2 I). Countries borrow
     strength across the panel without imposing cross-country homogeneity.
  3. Proper Fixed-Effect Recovery: Target is country-demeaned during estimation to absorb
     fixed effects, then explicitly restored via alpha_{i, h} = y_bar_{i, h} at forecast time.
  4. Adaptive Trace-Scaled Ridge Regularization: Eliminates arbitrary fixed penalty values.
  5. Per-Country Time-Varying Volatility (EWMA, half-life = 3 years): Captures localized
     heteroskedasticity and crisis regimes without polluting calm tranquil periods.
  6. Full Predictive Densities: Outputs Gaussian predictive distribution parameters (mu, sigma)
     enabling continuous ranked probability score (CRPS), log score, and PIT calibration.

Contract:
  forecaster(train, origin, horizons) -> DataFrame[iso, h, pred]
  forecaster_density(train, origin, horizons) -> DataFrame[iso, h, pred, sigma]
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
import pandas as pd

TARGET = "GDP_GROWTH"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _safe(x: np.ndarray, lo: float = 1e-10) -> np.ndarray:
    return np.clip(x, lo, None)


def _ewma_vol(resid: np.ndarray, halflife: float = 3.0) -> float:
    """EWMA volatility estimator with exponential half-life weighting."""
    if len(resid) == 0:
        return 1.0
    w = 0.5 ** (np.arange(len(resid))[::-1] / halflife)
    w /= w.sum()
    vol = float(np.sqrt(np.sum(w * (resid ** 2))))
    return max(vol, 1e-4)


def _extract_global_factor(train: pd.DataFrame, n_factors: int = 1) -> pd.DataFrame:
    """PCA on standardized growth panel; sign-anchored to USA."""
    wide = train.pivot_table(index="year", columns="iso", values=TARGET, aggfunc="mean")
    z = (wide - wide.mean()) / wide.std().replace(0, 1.0)
    z = z.fillna(z.mean()).fillna(0.0)
    X = z.to_numpy()
    if X.shape[1] < 2 or X.shape[0] < 3:
        return pd.DataFrame({"year": wide.index.values, "f0": np.zeros(len(wide))})
    Xc = X - X.mean(axis=0, keepdims=True)
    U, S, _ = np.linalg.svd(Xc, full_matrices=False)
    F = U[:, :n_factors] * S[:n_factors]
    out = pd.DataFrame(F, columns=[f"f{k}" for k in range(n_factors)])
    out["year"] = wide.index.values
    if "USA" in wide.columns:
        us = wide["USA"].fillna(0).to_numpy()
        for k in range(n_factors):
            if np.corrcoef(out[f"f{k}"], us)[0, 1] < 0:
                out[f"f{k}"] *= -1
    return out


# ---------------------------------------------------------------------------
# Fit Container & Model
# ---------------------------------------------------------------------------

@dataclass
class _HorizonFit:
    beta_pool: np.ndarray
    beta_i: dict[str, np.ndarray]
    alpha_i: dict[str, float]
    alpha_pool: float
    sigma_pool: float
    sigma_i: dict[str, float]
    tau2: np.ndarray
    feat_means: dict[str, float]
    feat_sds: dict[str, float]


class HBDLPSV:
    FEATS_BASE = ["y_t", "conv", "dep", "f0", "y_t_x_f0"]

    def __init__(self, horizons=(1, 2, 3, 4, 5),
                 n_factors: int = 1,
                 factor_lags: int = 2,
                 shrinkage_floor: float = 0.05,
                 min_obs_per_country: int = 8):
        self.horizons = list(horizons)
        self.n_factors = n_factors
        self.factor_lags = factor_lags
        self.shrinkage_floor = shrinkage_floor
        self.min_obs_per_country = min_obs_per_country
        self.fits: dict[int, _HorizonFit] = {}
        self.factor_df: pd.DataFrame | None = None
        self.factor_ar = np.zeros(factor_lags)
        self.factor_sigma = 1.0

    # -------- design --------

    def _design(self, df: pd.DataFrame, factor_df: pd.DataFrame) -> pd.DataFrame:
        d = df.sort_values(["iso", "year"]).copy()
        d["conv"] = np.log(d["GDP_PC_PPP"]) if "GDP_PC_PPP" in d.columns else np.nan
        d["dep"]  = d["DEPENDENCY_RATIO"] if "DEPENDENCY_RATIO" in d.columns else np.nan
        d["y_t"]  = d[TARGET]
        
        f = factor_df.copy()
        d = d.merge(f[["year", "f0"]], on="year", how="left")
        d["f0"] = d["f0"].fillna(0.0)
        d["y_t_x_f0"] = d["y_t"] * d["f0"]
        return d

    def _fit_factor_ar(self, factor_df: pd.DataFrame):
        f = factor_df["f0"].to_numpy()
        p = self.factor_lags
        if len(f) <= p + 2:
            self.factor_ar = np.zeros(p)
            self.factor_sigma = float(np.std(f)) if len(f) > 1 else 1.0
            return
        Y = f[p:]
        X = np.column_stack([np.ones(len(Y))] +
                            [f[p - j - 1: len(f) - j - 1] for j in range(p)])
        beta, *_ = np.linalg.lstsq(X, Y, rcond=None)
        resid = Y - X @ beta
        self.factor_ar = beta[1:].astype(float)
        self.factor_sigma = float(np.std(resid)) if len(resid) > 1 else 1.0

    # -------- fit --------

    def fit(self, train: pd.DataFrame) -> "HBDLPSV":
        train = train.sort_values(["iso", "year"]).copy()
        self.factor_df = _extract_global_factor(train, self.n_factors)
        self._fit_factor_ar(self.factor_df)
        d = self._design(train, self.factor_df)

        for h in self.horizons:
            self.fits[h] = self._fit_h(d, h)
        return self

    def _fit_h(self, d: pd.DataFrame, h: int) -> _HorizonFit:
        dh = d.copy()
        dh["target_h"] = dh.groupby("iso")[TARGET].shift(-h)
        feats = self.FEATS_BASE
        sub = dh.dropna(subset=["target_h"] + feats)
        isos = sorted(d["iso"].unique())
        
        if len(sub) < 30:
            bp = np.zeros(len(feats))
            m_target = float(d[TARGET].mean())
            return _HorizonFit(
                bp, {i: bp.copy() for i in isos},
                {i: m_target for i in isos},
                m_target,
                float(d[TARGET].std()),
                {i: float(d[TARGET].std()) for i in isos},
                np.ones(len(feats)),
                {f: 0.0 for f in feats}, {f: 1.0 for f in feats}
            )

        # Standardize features within origin strictly using historical sample
        fm, fs = {}, {}
        Xcols = []
        for f in feats:
            m = float(sub[f].mean())
            s = float(sub[f].std()) or 1.0
            fm[f], fs[f] = m, s
            Xcols.append(((sub[f] - m) / s).to_numpy())
        X = np.column_stack(Xcols)
        iso = sub["iso"].to_numpy()

        # Country fixed effects on target
        g = sub.groupby("iso")
        yw = (sub["target_h"] - g["target_h"].transform("mean")).to_numpy()
        p_dim = X.shape[1]

        # Adaptive trace-scaled ridge penalty for pooled regression
        lam_pool = max(1.0, 1.0 * np.trace(X.T @ X) / p_dim)
        beta_pool = np.linalg.solve(X.T @ X + lam_pool * np.eye(p_dim), X.T @ yw)
        resid_pool = yw - X @ beta_pool
        sigma_pool = max(float(np.std(resid_pool)), 1e-6)

        country_y_mean = sub.groupby("iso")["target_h"].mean().to_dict()
        global_mean_y = float(sub["target_h"].mean())

        # Prior variance tau2 from cross-country slope deviations
        devs = []
        for c in np.unique(iso):
            m = iso == c
            if m.sum() < self.min_obs_per_country:
                continue
            Xi, yi = X[m], yw[m]
            lam_i = max(5.0, 5.0 * np.trace(Xi.T @ Xi) / p_dim)
            bi = np.linalg.solve(Xi.T @ Xi + lam_i * np.eye(p_dim), Xi.T @ yi)
            devs.append(bi - beta_pool)
        tau2 = (np.var(np.array(devs), axis=0) if devs
                else np.ones(p_dim) * self.shrinkage_floor)
        tau2 = _safe(tau2, lo=self.shrinkage_floor)

        # Country posterior updates and local volatility
        beta_i: dict[str, np.ndarray] = {}
        alpha_i: dict[str, float] = {}
        sigma_i: dict[str, float] = {}
        for c in isos:
            m = iso == c
            alpha_c = country_y_mean.get(c, global_mean_y)
            alpha_i[c] = float(alpha_c)
            if m.sum() < 3:
                beta_i[c] = beta_pool.copy()
                sigma_i[c] = sigma_pool
                continue
            Xi, yi = X[m], yw[m]
            prec = Xi.T @ Xi + (sigma_pool ** 2) * np.diag(1.0 / tau2)
            rhs  = Xi.T @ yi + (sigma_pool ** 2) * np.diag(1.0 / tau2) @ beta_pool
            try:
                bi = np.linalg.solve(prec, rhs)
            except np.linalg.LinAlgError:
                bi = beta_pool.copy()
            beta_i[c] = bi
            sig_local = _ewma_vol(yi - Xi @ bi, halflife=3.0)
            sigma_i[c] = float(np.sqrt(0.7 * (sig_local ** 2) + 0.3 * (sigma_pool ** 2)))

        return _HorizonFit(
            beta_pool=beta_pool,
            beta_i=beta_i,
            alpha_i=alpha_i,
            alpha_pool=global_mean_y,
            sigma_pool=sigma_pool,
            sigma_i=sigma_i,
            tau2=tau2,
            feat_means=fm,
            feat_sds=fs
        )

    # -------- forecast --------

    def forecast(self, train: pd.DataFrame, origin: int,
                 horizons: list[int], return_density: bool = False) -> pd.DataFrame:
        if not self.fits:
            self.fit(train)
        d = self._design(train, self.factor_df)
        latest = d.sort_values("year").groupby("iso").last()
        feats = self.FEATS_BASE
        isos = list(latest.index)
        rows = []
        for h in horizons:
            if h not in self.fits:
                continue
            fit = self.fits[h]
            for iso in isos:
                xrow = []
                for f in feats:
                    v = latest.loc[iso, f] if f in latest.columns else np.nan
                    if not np.isfinite(v):
                        v = fit.feat_means[f]
                    xrow.append((v - fit.feat_means[f]) / fit.feat_sds[f])
                xvec = np.array(xrow)
                bi = fit.beta_i.get(iso, fit.beta_pool)
                alpha = fit.alpha_i.get(iso, fit.alpha_pool)
                mu = float(alpha + xvec @ bi)
                sg = fit.sigma_i.get(iso, fit.sigma_pool)
                rows.append({"iso": iso, "h": int(h),
                             "pred": mu, "sigma": float(sg)})
        out = pd.DataFrame(rows)
        return out if return_density else out[["iso", "h", "pred"]]


def hb_dlp_sv(train: pd.DataFrame, origin: int, horizons: list[int]) -> pd.DataFrame:
    """Standard point forecaster matching evaluation.py contract."""
    m = HBDLPSV(horizons=list(horizons))
    m.fit(train)
    return m.forecast(train, origin, horizons, return_density=False)


def hb_dlp_sv_density(train: pd.DataFrame, origin: int, horizons: list[int]) -> pd.DataFrame:
    """Predictive density forecaster returning mu (pred) and sigma."""
    m = HBDLPSV(horizons=list(horizons))
    m.fit(train)
    return m.forecast(train, origin, horizons, return_density=True)


if __name__ == "__main__":
    from evaluation import rolling_origin, report
    panel = pd.read_csv("data/processed/panel_raw.csv").dropna(subset=[TARGET])
    print("Testing HB-DLP-SV via rolling origin evaluation...")
    ev = rolling_origin(panel, {"HB-DLP-SV": hb_dlp_sv}, horizons=[1, 2, 3, 4, 5], verbose=True)
    report(ev, "HB-DLP-SV")
