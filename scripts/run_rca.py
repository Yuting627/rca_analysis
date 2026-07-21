#!/usr/bin/env python3
"""CLI for SKU RCA pipeline. Run parameters are read from the config file."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rca.pipeline import run_rca  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run SKU RCA. input/output/period/mode are read from config."
    )
    parser.add_argument(
        "--config",
        default=str(ROOT / "config" / "default.yaml"),
        help="Path to YAML config (default: config/default.yaml)",
    )
    args = parser.parse_args()

    df = run_rca(config_path=args.config)
    settings = df.attrs.get("settings", {})
    out = settings.get("out_path", "")
    print(f"Wrote {len(df)} rows to {out}")
    print(
        f"period={settings.get('period', 'n/a')} mode={settings.get('mode', 'n/a')} "
        f"market_sign={df['market_sign'].iloc[0] if len(df) else 'n/a'} "
        f"overall_delta={df['overall_delta_value'].iloc[0] if len(df) else 'n/a'}"
    )


if __name__ == "__main__":
    main()
