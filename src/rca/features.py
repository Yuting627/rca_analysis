"""Derived metrics for dual-value SKU monthly panel."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def add_features(df: pd.DataFrame, cfg: dict[str, Any]) -> pd.DataFrame:
    out = df.copy()
    w_r = float(cfg["weights"]["regular"])
    w_p = float(cfg["weights"]["promotion"])
    eps = float(cfg.get("epsilon", 1e-9))
    rolling = int(cfg["windows"]["rolling"])

    out["regular_value"] = out["unit"] * out["regular_price"]
    out["promotion_value"] = np.where(
        out["promo_price"].notna(),
        out["unit"] * out["promo_price"],
        np.nan,
    )
    out["value_gap"] = np.where(
        out["promo_price"].notna(),
        out["regular_value"] - out["promotion_value"],
        0.0,
    )
    out["discount_rate"] = np.where(
        out["promo_price"].notna() & (out["regular_price"] > 0),
        1.0 - out["promo_price"] / out["regular_price"],
        0.0,
    )
    out["avg_selling_proxy"] = np.where(
        out["promo_price"].notna(),
        (out["regular_price"] + out["promo_price"]) / 2.0,
        out["regular_price"],
    )
    out["weighted_value"] = np.where(
        out["promo_price"].notna(),
        w_r * out["regular_value"] + w_p * out["promotion_value"],
        out["regular_value"],
    )

    out = out.sort_values(["sku_id", "period"]).reset_index(drop=True)
    out["expected_unit"] = (
        out.groupby("sku_id", group_keys=False)["unit"]
        .apply(lambda s: s.shift(1).rolling(rolling, min_periods=1).mean())
    )
    out["incremental_unit"] = out["unit"] - out["expected_unit"]
    gap = out["value_gap"].abs()
    out["promo_efficiency"] = np.where(
        out["promo_price"].notna() & (gap > eps),
        (out["incremental_unit"] * out["avg_selling_proxy"]) / gap.clip(lower=eps),
        np.nan,
    )
    return out
