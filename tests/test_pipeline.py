from pathlib import Path

from rca.pipeline import run_rca, run_settings_from_config
from rca.schema import load_config

ROOT = Path(__file__).resolve().parents[1]


def test_settings_from_config():
    cfg_path = ROOT / "config" / "default.yaml"
    cfg = load_config(cfg_path)
    settings = run_settings_from_config(cfg, cfg_path)
    assert settings["period"] == "20261407"
    assert settings["mode"] == "yoy"
    assert settings["input_path"].name == "sku_monthly.csv"
    assert "priority" in settings["out_path"].name


def test_sample_pipeline_runs():
    cfg_path = ROOT / "config" / "default.yaml"
    df = run_rca(config_path=cfg_path)
    assert len(df) > 0
    assert "priority" in df.columns
    assert "promo_unit" not in df.columns
    assert df["market_sign"].nunique() == 1
    out = df.attrs["settings"]["out_path"]
    assert Path(out).exists()
