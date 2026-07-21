import pandas as pd

from rca.priority import compute_priority, rank_pct


def test_rank_pct_direction():
    s = pd.Series([1.0, 3.0, 2.0])
    r = rank_pct(s)
    assert r.iloc[1] > r.iloc[2] > r.iloc[0]


def test_priority_uses_aligned_not_abs():
    cfg = {"priority": {"top_n": 10}}
    df = pd.DataFrame(
        {
            "sku_id": ["big_drop", "big_up", "mid"],
            "aligned_contribution": [500.0, -100.0, 50.0],
            "total_contribution": [-500.0, 100.0, -50.0],
            "abnormal": [1.0, 4.0, 1.0],
            "trend_score": [0.1, 0.2, 0.05],
        }
    )
    out = compute_priority(df, cfg)
    # big_drop has highest aligned => should rank first by impact even if abnormal lower
    assert out.iloc[0]["sku_id"] == "big_drop"
    assert out.loc[out["sku_id"] == "big_up", "impact_n"].iloc[0] < out.loc[
        out["sku_id"] == "big_drop", "impact_n"
    ].iloc[0]
