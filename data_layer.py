#!/usr/bin/env python3
"""
Data acquisition layer.

Everything here is re-downloadable from public sources with no authentication. The API
quirks encoded below were each discovered the hard way in a previous project and are the
reason this module exists rather than a few inline requests calls:

  * The World Governance Indicators (GE.EST, CC.EST, RQ.EST, RL.EST) have been ARCHIVED
    out of the ordinary WDI endpoint and return "The indicator was not found. It may have
    been deleted or archived." They must be requested as GOV_WGI_<CODE> against source=3.
    A previous pipeline silently lost its entire governance measure to this and went on
    describing the affected dimension as "institutional quality".
  * TX.VAL.TEXT.ZS.UN (textile export share) returns "parameter value is not valid" for
    every country. It does not exist.
  * High-technology exports (TX.VAL.TECH.MF.ZS) is effectively empty before ~2005, and
    R&D (GB.XPD.RSDV.GD.ZS) before ~1995.
  * Penn World Table is PWT 10.01 (1950-2019), not 11.0; the file commonly named
    pwt110.xlsx is 10.01. It is served from dataverse.nl.

Design rules:
  * Every response is cached to disk and hashed. Re-runs are offline and byte-identical.
  * An indicator that returns nothing is REPORTED, never silently dropped.
  * The WLD world aggregate is fetched alongside the countries, because world growth is a
    genuine fast-moving predictor and the single most obvious omission from the previous
    model's slow-moving structural indicator set.
"""

import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "processed"
for d in (RAW, PROC):
    d.mkdir(parents=True, exist_ok=True)

WB = "https://api.worldbank.org/v2"
UA = {"User-Agent": "growth-forecast-research/1.0"}

COUNTRIES = ["JPN", "BGD", "KOR", "SGP", "CHN", "MYS", "THA", "VNM", "IND", "IDN",
             "PHL", "DEU", "USA", "GBR", "FRA", "NLD"]

START, END = 1990, 2024

# ---------------------------------------------------------------------------
# Indicators. Grouped by how fast they move, because that distinction is the whole
# point: the previous model used only the bottom group and had nothing left with which
# to predict short-horizon fluctuation.
# ---------------------------------------------------------------------------
FAST = {                                   # cyclical / annual-frequency signal
    "GDP_GROWTH":        "NY.GDP.MKTP.KD.ZG",
    "EXPORT_GROWTH":     "NE.EXP.GNFS.KD.ZG",
    "IMPORT_GROWTH":     "NE.IMP.GNFS.KD.ZG",
    "INFLATION":         "FP.CPI.TOTL.ZG",
    "CREDIT_PRIVATE":    "FS.AST.PRVT.GD.ZS",
    "CURRENT_ACCOUNT":   "BN.CAB.XOKA.GD.ZS",
    "RESERVES_MONTHS":   "FI.RES.TOTL.MO",
    "TERMS_OF_TRADE":    "TT.PRI.MRCH.XD.WD",
    "UNEMPLOYMENT":      "SL.UEM.TOTL.ZS",
    "GROSS_SAVINGS":     "NY.GNS.ICTR.ZS",
    "REAL_INTEREST":     "FR.INR.RINR",
    "EXCHANGE_RATE":     "PA.NUS.FCRF",
}

SLOW = {                                   # structural stocks
    "GDP_PC_PPP":        "NY.GDP.PCAP.PP.KD",
    "INVESTMENT":        "NE.GDI.TOTL.ZS",
    "FDI":               "BX.KLT.DINV.WD.GD.ZS",
    "TRADE_OPENNESS":    "NE.TRD.GNFS.ZS",
    "ELECTRICITY":       "EG.ELC.ACCS.ZS",
    "LIFE_EXPECTANCY":   "SP.DYN.LE00.IN",
    "SCHOOLING_SEC":     "SE.SEC.ENRR",
    "RND":               "GB.XPD.RSDV.GD.ZS",
    "HIGH_TECH_EXPORTS": "TX.VAL.TECH.MF.ZS",
    "TAX_REVENUE":       "GC.TAX.TOTL.GD.ZS",
    "REVENUE_EX_GRANTS": "GC.REV.XGRT.GD.ZS",
    "DEPENDENCY_RATIO":  "SP.POP.DPND",
    "POPULATION":        "SP.POP.TOTL",
    "MANUF_VA":          "NV.IND.MANF.ZS",
    "URBAN_SHARE":       "SP.URB.TOTL.IN.ZS",
}

# Worldwide Governance Indicators. MUST go through source=3 with the GOV_WGI_ prefix.
WGI = {
    "GOV_EFFECTIVENESS": "GOV_WGI_GE.EST",
    "REG_QUALITY":       "GOV_WGI_RQ.EST",
    "RULE_OF_LAW":       "GOV_WGI_RL.EST",
    "CONTROL_CORRUPTION": "GOV_WGI_CC.EST",
    "POLITICAL_STABILITY": "GOV_WGI_PV.EST",
}

ALL_WDI = {**FAST, **SLOW}

PWT_URL = "https://dataverse.nl/api/access/datafile/354095"
PWT_FILE = ROOT / "data" / "pwt1001.xlsx"


def _cache_path(iso, code):
    return RAW / f"{iso}_{code.replace('.', '_')}_{START}_{END}.json"


def fetch_series(iso, code, source=None, retries=3):
    """Fetch one country-indicator series, cached. Returns (rows, status)."""
    cp = _cache_path(iso, code)
    if cp.exists():
        try:
            js = json.loads(cp.read_text(encoding="utf-8"))
            rows = js[1] if len(js) > 1 and js[1] else []
            return rows, "cached"
        except Exception:
            pass

    params = {"format": "json", "per_page": 20000, "date": f"{START}:{END}"}
    if source:
        params["source"] = str(source)
    url = f"{WB}/country/{iso}/indicator/{code}"

    for attempt in range(retries):
        try:
            r = requests.get(url, params=params, headers=UA, timeout=45)
            r.raise_for_status()
            js = r.json()
            if isinstance(js, list) and js and isinstance(js[0], dict) and "message" in js[0]:
                msg = js[0]["message"]
                return [], f"api_error: {msg[0].get('value', '')[:60] if isinstance(msg, list) else msg}"
            cp.write_text(json.dumps(js), encoding="utf-8")
            rows = js[1] if len(js) > 1 and js[1] else []
            return rows, "fetched"
        except Exception as e:
            if attempt == retries - 1:
                return [], f"failed: {type(e).__name__}"
            time.sleep(1.5 * (attempt + 1))
    return [], "failed"


def download_wdi(verbose=True):
    """Fetch every configured indicator for every country plus the WLD aggregate."""
    records, status = [], {}
    targets = COUNTRIES + ["WLD"]
    jobs = ([(n, c, None) for n, c in ALL_WDI.items()]
            + [(n, c, 3) for n, c in WGI.items()])

    total = len(jobs) * len(targets)
    done = 0
    for name, code, source in jobs:
        got_any = 0
        for iso in targets:
            rows, st = fetch_series(iso, code, source=source)
            done += 1
            for r in rows:
                v = r.get("value")
                if v is not None:
                    records.append({"iso": iso, "year": int(r["date"]),
                                    "indicator": name, "value": float(v)})
                    got_any += 1
            if done % 60 == 0 and verbose:
                print(f"    ...{done}/{total} series")
        status[name] = {"code": code, "source": source, "observations": got_any}
        if got_any == 0:
            print(f"  !! {name} ({code}) RETURNED NOTHING -- it is absent from every "
                  f"downstream model. Do not describe any construct as containing it.")

    df = pd.DataFrame(records)
    (RAW / "availability.json").write_text(json.dumps(status, indent=2), encoding="utf-8")

    manifest = {}
    for f in sorted(RAW.glob("*.json")):
        if f.name in ("availability.json", "manifest.json"):
            continue
        manifest[f.name] = hashlib.sha256(f.read_bytes()).hexdigest()
    (RAW / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    if verbose:
        print(f"  cached {len(manifest)} files with SHA-256 manifest")
    return df, status


def download_pwt(verbose=True):
    """Penn World Table 10.01 (1950-2019). Named honestly, unlike the usual pwt110.xlsx."""
    if not PWT_FILE.exists():
        if verbose:
            print("  downloading PWT 10.01 ...")
        r = requests.get(PWT_URL, headers=UA, timeout=180)
        r.raise_for_status()
        PWT_FILE.write_bytes(r.content)
    x = pd.read_excel(PWT_FILE, sheet_name="Data")
    keep = [c for c in ["countrycode", "year", "ctfp", "hc", "rkna", "emp", "pop",
                        "cgdpo", "rgdpo", "rgdpna", "labsh"] if c in x.columns]
    x = x[keep].rename(columns={"countrycode": "iso"})
    x = x[x["iso"].isin(COUNTRIES) & x["year"].between(START, END)]
    if verbose:
        print(f"  PWT 10.01: {len(x)} rows, {x.year.min()}-{x.year.max()} "
              f"(note: ends 2019; later years are NOT available and must not be imputed "
              f"without a flag)")
    return x


def build_panel(verbose=True):
    """Assemble the analysis panel. No imputation, no normalisation -- raw observations
    only. Every modelling transform belongs downstream where it can be refit per
    rolling-origin fold without leaking future information."""
    if verbose:
        print("[1/3] World Bank (WDI + WGI source=3)...")
    long, status = download_wdi(verbose=verbose)
    if long.empty:
        sys.exit("No data retrieved.")

    wide = long.pivot_table(index=["iso", "year"], columns="indicator",
                            values="value", aggfunc="first").reset_index()

    world = wide[wide.iso == "WLD"].set_index("year")
    panel = wide[wide.iso != "WLD"].copy()

    # GLOBAL FACTOR: world growth and world trade, aligned by year. The single most
    # obvious fast-moving predictor of a small open economy's annual growth, and entirely
    # absent from the previous model.
    for src, dst in [("GDP_GROWTH", "WORLD_GROWTH"),
                     ("EXPORT_GROWTH", "WORLD_EXPORT_GROWTH"),
                     ("INFLATION", "WORLD_INFLATION")]:
        if src in world.columns:
            panel[dst] = panel["year"].map(world[src])

    if verbose:
        print("[2/3] Penn World Table...")
    try:
        pwt = download_pwt(verbose=verbose)
        panel = panel.merge(pwt, on=["iso", "year"], how="left")
    except Exception as e:
        print(f"  WARNING: PWT unavailable ({e}); continuing without it")

    if verbose:
        print("[3/3] Writing panel...")
    panel = panel.sort_values(["iso", "year"]).reset_index(drop=True)
    out = PROC / "panel_raw.csv"
    panel.to_csv(out, index=False)

    cov = []
    for c in panel.columns:
        if c in ("iso", "year"):
            continue
        cov.append({"variable": c,
                    "non_null": int(panel[c].notna().sum()),
                    "coverage": float(panel[c].notna().mean()),
                    "first_year": (int(panel.loc[panel[c].notna(), "year"].min())
                                   if panel[c].notna().any() else None),
                    "n_countries": int(panel.loc[panel[c].notna(), "iso"].nunique())})
    covdf = pd.DataFrame(cov).sort_values("coverage", ascending=False)
    covdf.to_csv(PROC / "coverage_report.csv", index=False)

    if verbose:
        print(f"\nPanel: {len(panel)} rows, {panel.iso.nunique()} countries, "
              f"{panel.year.min()}-{panel.year.max()}, {len(panel.columns) - 2} variables")
        print(f"Written: {out}")
        print("\nCoverage (top 20):")
        print(covdf.head(20).to_string(index=False))
        weak = covdf[covdf.coverage < 0.5]
        if len(weak):
            print(f"\n{len(weak)} variables below 50% coverage -- candidates for exclusion:")
            print(weak[["variable", "coverage", "first_year"]].to_string(index=False))
    return panel


if __name__ == "__main__":
    build_panel()
