"""Shapley dual-track contribution with market_sign."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from rca.period import parse_period


def shapley_unit_price(u0: float, p0: float, u1: float, p1: float) -> tuple[float, float]:
    c_unit = (u1 - u0) * (p0 + p1) / 2.0
    c_price = (p1 - p0) * (u0 + u1) / 2.0
    return c_unit, c_price


def market_sign_from_overall(overall_delta: float, eps: float) -> int:
    if overall_delta > eps:
        return 1
    return -1


def compute_contributions(
    df: pd.DataFrame,
    period: str,
    cfg: dict[str, Any],
    mode: str = "yoy",
) -> pd.DataFrame:
    """Compute MoM or YoY Shapley contributions for report period."""
    eps = float(cfg.get("epsilon", 1e-9))
    w_r = float(cfg["weights"]["regular"])
    w_p = float(cfg["weights"]["promotion"])

    p1 = parse_period(period)
    base = p1.yoy() if mode == "yoy" else p1.mom()
    p0_str = base.format()
    p1_str = p1.format()

    cur = df[df["period"] == p1_str].set_index("sku_id")
    prev = df[df["period"] == p0_str].set_index("sku_id")
    if cur.empty:
        raise ValueError(f"no rows for report period {p1_str}")
    if prev.empty:
        raise ValueError(f"no rows for base period {p0_str} ({mode})")

    skus = cur.index.intersection(prev.index)
    rows: list[dict[str, Any]] = []
    for sku in skus:
        r1 = cur.loc[sku]
        r0 = prev.loc[sku]
        u0, u1 = float(r0["unit"]), float(r1["unit"])
        preg0, preg1 = float(r0["regular_price"]), float(r1["regular_price"])

        u_reg, p_reg = shapley_unit_price(u0, preg0, u1, preg1)
        d_reg = u_reg + p_reg

        promo0 = r0["promo_price"]
        promo1 = r1["promo_price"]
        if pd.notna(promo0) and pd.notna(promo1):
            u_pro, p_pro = shapley_unit_price(u0, float(promo0), u1, float(promo1))
            d_pro = u_pro + p_pro
        else:
            u_pro, p_pro, d_pro = 0.0, 0.0, 0.0

        total = w_r * d_reg + w_p * d_pro
        unit_c = w_r * u_reg + w_p * u_pro
        rows.append(
            {
                "sku_id": sku,
                "period": p1_str,
                "base_period": p0_str,
                "mode": mode,
                "unit": u1,
                "unit_0": u0,
                "regular_price": preg1,
                "regular_price_0": preg0,
                "promo_price": promo1 if pd.notna(promo1) else np.nan,
                "promo_price_0": promo0 if pd.notna(promo0) else np.nan,
                "regular_value": float(r1["regular_value"]),
                "promotion_value": float(r1["promotion_value"])
                if pd.notna(r1["promotion_value"])
                else np.nan,
                "weighted_value": float(r1["weighted_value"]),
                "value_gap": float(r1["value_gap"]),
                "discount_rate": float(r1["discount_rate"]),
                "promo_efficiency": float(r1["promo_efficiency"])
                if pd.notna(r1["promo_efficiency"])
                else np.nan,
                "unit_contrib_regular": u_reg,
                "price_contrib_regular": p_reg,
                "delta_regular_value": d_reg,
                "unit_contrib_promotion": u_pro,
                "price_contrib_promotion": p_pro,
                "delta_promotion_value": d_pro,
                "unit_contrib": unit_c,
                "regular_price_contrib": w_r * p_reg,
                "promo_price_contrib": w_p * p_pro,
                "total_contribution": total,
                "delta_unit": u1 - u0,
                "delta_regular_price": preg1 - preg0,
                "delta_promo_price": (
                    float(promo1) - float(promo0)
                    if pd.notna(promo0) and pd.notna(promo1)
                    else np.nan
                ),
                "delta_discount_rate": float(r1["discount_rate"]) - float(r0["discount_rate"]),
            }
        )

    out = pd.DataFrame(rows)
    overall = float(out["total_contribution"].sum())
    sign = market_sign_from_overall(overall, eps)
    out["overall_delta_value"] = overall
    out["market_sign"] = sign
    out["aligned_contribution"] = sign * out["total_contribution"]
    if abs(overall) > eps:
        out["contribution_pct"] = out["total_contribution"] / overall * 100.0
    else:
        out["contribution_pct"] = np.nan
    return out
