"""End-to-end RCA pipeline."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from rca.abnormality import add_zscores, attach_abnormal
from rca.contribution import compute_contributions
from rca.diagnose import attach_diagnosis
from rca.features import add_features
from rca.io import read_sku_monthly, write_output
from rca.period import parse_period
from rca.priority import compute_priority
from rca.promotion import attach_promo_drivers
from rca.schema import load_config
from rca.trend import attach_trend

OUTPUT_COLUMNS = [
    "sku_id",
    "priority",
    "rank",
    "market_sign",
    "overall_delta_value",
    "total_contribution",
    "aligned_contribution",
    "contribution_pct",
    "unit_contrib",
    "regular_price_contrib",
    "promo_price_contrib",
    "delta_regular_value",
    "delta_promotion_value",
    "unit_contrib_regular",
    "price_contrib_regular",
    "unit_contrib_promotion",
    "price_contrib_promotion",
    "regular_value",
    "promotion_value",
    "weighted_value",
    "value_gap",
    "abnormal",
    "trend_score",
    "yoy",
    "mom",
    "discount_rate",
    "promo_efficiency",
    "primary_driver",
    "sub_driver",
    "action_code",
    "action_text",
]


def run_rca(
    input_path: str | Path,
    period: str,
    config_path: str | Path,
    out_path: str | Path | None = None,
    mode: str = "mom",
) -> pd.DataFrame:
    cfg = load_config(config_path)
    period = parse_period(period).format()

    raw = read_sku_monthly(input_path, cfg)
    panel = add_features(raw, cfg)
    panel = add_zscores(panel, cfg)

    contrib = compute_contributions(panel, period, cfg, mode=mode)
    contrib = attach_abnormal(contrib, panel)
    contrib = attach_trend(contrib, panel, cfg)
    contrib = attach_promo_drivers(contrib)
    scored = compute_priority(contrib, cfg)
    diagnosed = attach_diagnosis(scored, cfg)

    top_n = int(cfg.get("priority", {}).get("top_n", 50))
    result = diagnosed.head(top_n).copy()
    cols = [c for c in OUTPUT_COLUMNS if c in result.columns]
    result = result[cols]

    if out_path is not None:
        write_output(result, out_path)
    return result
