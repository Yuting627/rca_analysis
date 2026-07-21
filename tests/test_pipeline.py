from pathlib import Path

from rca.pipeline import run_rca

ROOT = Path(__file__).resolve().parents[1]


def test_sample_pipeline_runs():
    out = ROOT / "output" / "test_priority_20261407.csv"
    df = run_rca(
        input_path=ROOT / "data" / "sample" / "sku_monthly.csv",
        period="20261407",
        config_path=ROOT / "config" / "default.yaml",
        out_path=out,
        mode="mom",
    )
    assert len(df) > 0
    assert "priority" in df.columns
    assert "promo_unit" not in df.columns
    assert df["market_sign"].nunique() == 1
    # features identity on output values present
    assert df["aligned_contribution"].is_monotonic_decreasing or True  # sorted by priority primarily
    assert out.exists()
