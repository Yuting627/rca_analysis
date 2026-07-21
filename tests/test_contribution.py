import pandas as pd

from rca.contribution import compute_contributions, market_sign_from_overall, shapley_unit_price
from rca.features import add_features


def test_shapley_example():
    c_u, c_p = shapley_unit_price(100, 10, 120, 12)
    assert abs(c_u - 220) < 1e-9
    assert abs(c_p - 220) < 1e-9
    assert abs(c_u + c_p - 440) < 1e-9


def test_market_sign():
    assert market_sign_from_overall(10, 1e-9) == 1
    assert market_sign_from_overall(-10, 1e-9) == -1
    assert market_sign_from_overall(0, 1e-9) == -1


def test_dual_track_identity_and_direction():
    cfg = {
        "weights": {"regular": 0.5, "promotion": 0.5},
        "windows": {"rolling": 12, "min_history": 6},
        "epsilon": 1e-9,
    }
    data = [
        {"sku_id": "A", "period": "20261406", "unit": 100, "regular_price": 10, "promo_price": 8},
        {"sku_id": "A", "period": "20261407", "unit": 80, "regular_price": 10, "promo_price": 8},
        {"sku_id": "B", "period": "20261406", "unit": 50, "regular_price": 10, "promo_price": 9},
        {"sku_id": "B", "period": "20261407", "unit": 60, "regular_price": 10, "promo_price": 9},
    ]
    df = add_features(pd.DataFrame(data), cfg)
    out = compute_contributions(df, "20261407", cfg, mode="mom")
    assert out["market_sign"].iloc[0] == -1
    assert out["overall_delta_value"].iloc[0] < 0
    a = out.set_index("sku_id").loc["A"]
    b = out.set_index("sku_id").loc["B"]
    assert a["total_contribution"] < b["total_contribution"]
    assert a["aligned_contribution"] > b["aligned_contribution"]
    for _, r in out.iterrows():
        assert abs(r["delta_regular_value"] - (r["unit_contrib_regular"] + r["price_contrib_regular"])) < 1e-8
        assert abs(r["delta_promotion_value"] - (r["unit_contrib_promotion"] + r["price_contrib_promotion"])) < 1e-8


def test_up_market_direction():
    cfg = {
        "weights": {"regular": 0.5, "promotion": 0.5},
        "windows": {"rolling": 12, "min_history": 6},
        "epsilon": 1e-9,
    }
    data = [
        {"sku_id": "A", "period": "20261406", "unit": 100, "regular_price": 10, "promo_price": 8},
        {"sku_id": "A", "period": "20261407", "unit": 130, "regular_price": 10, "promo_price": 8},
        {"sku_id": "B", "period": "20261406", "unit": 50, "regular_price": 10, "promo_price": 9},
        {"sku_id": "B", "period": "20261407", "unit": 45, "regular_price": 10, "promo_price": 9},
    ]
    df = add_features(pd.DataFrame(data), cfg)
    out = compute_contributions(df, "20261407", cfg, mode="mom")
    assert out["market_sign"].iloc[0] == 1
    a = out.set_index("sku_id").loc["A"]
    b = out.set_index("sku_id").loc["B"]
    assert a["aligned_contribution"] > b["aligned_contribution"]
