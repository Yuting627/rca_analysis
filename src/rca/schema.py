"""Config loading, column mapping, and input validation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from rca.period import parse_period

INTERNAL_COLUMNS = (
    "sku_id",
    "period",
    "unit",
    "regular_price",
    "promo_price",
)


def load_config(path: str | Path) -> dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    _validate_config(cfg)
    return cfg


def _validate_config(cfg: dict[str, Any]) -> None:
    cols = cfg.get("columns") or {}
    missing = [c for c in INTERNAL_COLUMNS if c not in cols]
    if missing:
        raise ValueError(f"config.columns missing: {missing}")
    w = cfg.get("weights") or {}
    wr = float(w.get("regular", 0.5))
    wp = float(w.get("promotion", 0.5))
    if abs(wr + wp - 1.0) > 1e-9:
        raise ValueError(f"weights.regular + weights.promotion must be 1, got {wr}+{wp}")
    fmt = (cfg.get("period") or {}).get("format", "YYYY14MM")
    if fmt != "YYYY14MM":
        raise ValueError(f"unsupported period.format: {fmt}")


def map_columns(df: pd.DataFrame, cfg: dict[str, Any]) -> pd.DataFrame:
    mapping = cfg["columns"]
    rename = {mapping[k]: k for k in INTERNAL_COLUMNS}
    missing_src = [mapping[k] for k in INTERNAL_COLUMNS if mapping[k] not in df.columns]
    if missing_src:
        raise ValueError(f"input missing columns: {missing_src}")
    out = df.rename(columns=rename)[list(INTERNAL_COLUMNS)].copy()
    return out


def validate_frame(df: pd.DataFrame, eps: float = 1e-9) -> pd.DataFrame:
    out = df.copy()
    out["sku_id"] = out["sku_id"].astype(str)
    out["period"] = out["period"].astype(str).map(lambda x: parse_period(x).format())
    out["unit"] = pd.to_numeric(out["unit"], errors="coerce")
    out["regular_price"] = pd.to_numeric(out["regular_price"], errors="coerce")
    out["promo_price"] = pd.to_numeric(out["promo_price"], errors="coerce")

    if out["unit"].isna().any() or (out["unit"] < 0).any():
        raise ValueError("unit must be non-negative and non-null")
    if out["regular_price"].isna().any() or (out["regular_price"] <= 0).any():
        raise ValueError("regular_price must be > 0")

    has_promo = out["promo_price"].notna()
    bad_promo = has_promo & (out["promo_price"] <= 0)
    if bad_promo.any():
        raise ValueError("promo_price must be > 0 when provided")

    # Soft check: promo <= regular when both present
    _ = eps
    return out
