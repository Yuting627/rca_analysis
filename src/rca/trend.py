"""Peer-relative trend score with market_sign."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from rca.period import parse_period


def attach_trend(contrib: pd.DataFrame, panel: pd.DataFrame, cfg: dict[str, Any]) -> pd.DataFrame:
    _ = cfg
    out = contrib.copy()
    period = str(out["period"].iloc[0])
    p1 = parse_period(period)
    p_mom = p1.mom().format()
    p_yoy = p1.yoy().format()

    wv = panel.set_index(["sku_id", "period"])["weighted_value"]
    yoy_list = []
    mom_list = []
    for sku in out["sku_id"]:
        try:
            v1 = float(wv.loc[(sku, period)])
        except KeyError:
            yoy_list.append(np.nan)
            mom_list.append(np.nan)
            continue
        try:
            v0m = float(wv.loc[(sku, p_mom)])
            mom_list.append(v1 / v0m - 1.0 if abs(v0m) > 1e-12 else np.nan)
        except KeyError:
            mom_list.append(np.nan)
        try:
            v0y = float(wv.loc[(sku, p_yoy)])
            yoy_list.append(v1 / v0y - 1.0 if abs(v0y) > 1e-12 else np.nan)
        except KeyError:
            yoy_list.append(np.nan)

    out["yoy"] = yoy_list
    out["mom"] = mom_list
    med_yoy = np.nanmedian(out["yoy"].to_numpy(dtype=float))
    med_mom = np.nanmedian(out["mom"].to_numpy(dtype=float))
    rel_yoy = out["yoy"] - med_yoy
    rel_mom = out["mom"] - med_mom

    trend_raw = []
    for ry, rm in zip(rel_yoy, rel_mom):
        if pd.notna(ry) and pd.notna(rm):
            trend_raw.append(0.6 * float(ry) + 0.4 * float(rm))
        elif pd.notna(rm):
            trend_raw.append(float(rm))
        elif pd.notna(ry):
            trend_raw.append(float(ry))
        else:
            trend_raw.append(np.nan)
    out["trend_raw"] = trend_raw

    scores = []
    for raw, sign in zip(out["trend_raw"], out["market_sign"]):
        if pd.isna(raw):
            scores.append(0.0)
        else:
            scores.append(float(max(0.0, int(sign) * float(raw))))
    out["trend_score"] = scores
    return out
