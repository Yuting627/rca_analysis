"""Primary driver and action rules with market_sign."""

from __future__ import annotations

from typing import Any

import pandas as pd


DRIVER_MAP = {
    "unit_contrib": "UNIT",
    "regular_price_contrib": "REGULAR_PRICE",
    "promo_price_contrib": "PROMO_PRICE",
}

ACTIONS = {
    "DEMAND_MOVE_WITH_DISCOUNT": (
        "TIGHTEN_DISCOUNT",
        "折扣与销量同向异动，建议将折扣收至历史中位附近并观察销量反应。",
    ),
    "ORGANIC_DEMAND_MOVE": (
        "HOLD_PRICE_PUSH_VOLUME",
        "价格结构平稳而销量主导变动，优先排查需求/铺货，暂不大幅调价。",
    ),
    "DEMAND_MOVE_VS_PROMO_PRICE": (
        "REVIEW_PROMO_PRICE",
        "销量与促销价逆向变动，建议复核促销价与折扣深度。",
    ),
    "REGULAR_PRICE_VOLUME_TRADEOFF": (
        "REVIEW_REGULAR_PRICE",
        "常规价与销量呈反向权衡，建议复核常规价变动幅度。",
    ),
    "PROMO_PRICE_EFFICIENCY_ISSUE": (
        "TIGHTEN_DISCOUNT",
        "促销折扣加剧且效率不利，建议收窄折扣并评估促销效率。",
    ),
    "MONITOR": (
        "MONITOR",
        "异常信号较弱，建议持续监控。",
    ),
}


def _pick_primary(row: pd.Series, market_sign: int) -> str:
    scores = {
        "unit_contrib": market_sign * float(row["unit_contrib"]),
        "regular_price_contrib": market_sign * float(row["regular_price_contrib"]),
        "promo_price_contrib": market_sign * float(row["promo_price_contrib"]),
    }
    key = max(scores, key=scores.get)
    return DRIVER_MAP[key]


def _sub_driver(row: pd.Series, primary: str, market_sign: int, thr: float) -> str:
    z_unit = row.get("z_unit")
    z_ok = pd.notna(z_unit) and (market_sign * float(z_unit) > thr)
    d_disc = float(row.get("delta_discount_rate") or 0.0)
    d_promo = row.get("delta_promo_price")
    disc_same = market_sign * d_disc > 0  # 跌市折扣加深为正贡献侧
    disc_flat = abs(d_disc) < 0.01
    promo_against = pd.notna(d_promo) and (market_sign * float(d_promo) < 0)

    if primary == "UNIT":
        if z_ok and disc_same and not disc_flat:
            return "DEMAND_MOVE_WITH_DISCOUNT"
        if z_ok and promo_against:
            return "DEMAND_MOVE_VS_PROMO_PRICE"
        if z_ok:
            return "ORGANIC_DEMAND_MOVE"
        return "ORGANIC_DEMAND_MOVE"

    if primary == "REGULAR_PRICE":
        d_p = float(row.get("delta_regular_price") or 0.0)
        d_u = float(row.get("delta_unit") or 0.0)
        if d_p * d_u < 0:
            return "REGULAR_PRICE_VOLUME_TRADEOFF"
        return "REGULAR_PRICE_VOLUME_TRADEOFF"

    if primary == "PROMO_PRICE":
        eff = row.get("promo_efficiency")
        # 不利效率：跌市 efficiency 偏低/下降；简化用 NaN 或负向
        if disc_same and (pd.isna(eff) or float(eff) < 0):
            return "PROMO_PRICE_EFFICIENCY_ISSUE"
        return "PROMO_PRICE_EFFICIENCY_ISSUE"

    return "MONITOR"


def attach_diagnosis(df: pd.DataFrame, cfg: dict[str, Any]) -> pd.DataFrame:
    thr = float(cfg.get("z_threshold", 2.0))
    out = df.copy()
    primaries = []
    subs = []
    codes = []
    texts = []
    for _, row in out.iterrows():
        sign = int(row["market_sign"])
        primary = _pick_primary(row, sign)
        sub = _sub_driver(row, primary, sign, thr)
        if float(row.get("abnormal") or 0) < 0.5 and float(row.get("trend_score") or 0) < 0.05:
            sub = "MONITOR"
        code, text = ACTIONS.get(sub, ACTIONS["MONITOR"])
        primaries.append(primary)
        subs.append(sub)
        codes.append(code)
        texts.append(text)
    out["primary_driver"] = primaries
    out["sub_driver"] = subs
    out["action_code"] = codes
    out["action_text"] = texts
    return out
