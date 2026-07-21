"""Promotion price driver fields (already largely on contribution/features)."""

from __future__ import annotations

import pandas as pd


def attach_promo_drivers(contrib: pd.DataFrame) -> pd.DataFrame:
    """Ensure promo driver columns exist for diagnose; z_* already merged."""
    out = contrib.copy()
    for col in ("discount_rate", "value_gap", "promo_efficiency", "z_discount_rate", "z_value_gap", "z_promo_price"):
        if col not in out.columns:
            out[col] = pd.NA
    return out
