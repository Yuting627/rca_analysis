"""Priority score from direction-aligned impact, abnormal, trend."""

from __future__ import annotations

from typing import Any

import pandas as pd


def rank_pct(series: pd.Series) -> pd.Series:
    """Percentile rank in [0, 1]; higher value -> higher rank."""
    if series.empty:
        return series
    return series.rank(method="average", pct=True)


def compute_priority(df: pd.DataFrame, cfg: dict[str, Any]) -> pd.DataFrame:
    out = df.copy()
    out["impact_n"] = rank_pct(out["aligned_contribution"])
    out["abn_n"] = (out["abnormal"] / 3.0).clip(upper=1.0)
    out["trend_n"] = (out["trend_score"] / 0.3).clip(upper=1.0)
    out["priority"] = (
        100.0
        * out["impact_n"]
        * (0.4 + 0.6 * out["abn_n"])
        * (0.5 + 0.5 * out["trend_n"])
    )
    out = out.sort_values(
        ["priority", "aligned_contribution", "sku_id"],
        ascending=[False, False, True],
    ).reset_index(drop=True)

    top_n = int(cfg.get("priority", {}).get("top_n", 50))
    out["rank"] = range(1, len(out) + 1)
    out.attrs["top_n"] = top_n
    return out
