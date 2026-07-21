"""Rolling z-scores and direction-aware abnormality."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


Z_COLS = (
    "unit",
    "regular_price",
    "promo_price",
    "regular_value",
    "promotion_value",
    "discount_rate",
    "value_gap",
)


def severity_z(z: float | np.floating, market_sign: int) -> float:
    if pd.isna(z):
        return 0.0
    return float(max(0.0, market_sign * float(z)))


def _rolling_z(series: pd.Series, window: int, min_hist: int, eps: float) -> pd.Series:
    prev = series.shift(1)
    mean = prev.rolling(window, min_periods=min_hist).mean()
    std = prev.rolling(window, min_periods=min_hist).std(ddof=0)
    std = std.where(std.abs() > eps, eps)
    return (series - mean) / std


def add_zscores(df: pd.DataFrame, cfg: dict[str, Any]) -> pd.DataFrame:
    out = df.sort_values(["sku_id", "period"]).copy()
    window = int(cfg["windows"]["rolling"])
    min_hist = int(cfg["windows"]["min_history"])
    eps = float(cfg.get("epsilon", 1e-9))

    for col in Z_COLS:
        zname = f"z_{col}"
        out[zname] = np.nan
        for sku, g in out.groupby("sku_id"):
            idx = g.index
            out.loc[idx, zname] = _rolling_z(g[col], window, min_hist, eps).to_numpy()
    return out


def attach_abnormal(contrib: pd.DataFrame, panel: pd.DataFrame) -> pd.DataFrame:
    """Merge period z-scores onto contribution rows and compute abnormal."""
    z_cols = [f"z_{c}" for c in Z_COLS]
    keep = ["sku_id", "period", *z_cols]
    zpanel = panel[keep].copy()
    out = contrib.merge(zpanel, on=["sku_id", "period"], how="left")

    abn_vals = []
    for _, r in out.iterrows():
        sign = int(r["market_sign"])
        parts = [
            severity_z(r.get(f"z_{c}"), sign)
            for c in Z_COLS
        ]
        abn_vals.append(float(np.clip(max(parts) if parts else 0.0, 0.0, 5.0)))
    out["abnormal"] = abn_vals
    return out
