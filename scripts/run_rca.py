#!/usr/bin/env python3
"""CLI for SKU RCA pipeline."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rca.pipeline import run_rca  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Run SKU RCA priority ranking")
    parser.add_argument("--input", required=True, help="Input CSV path")
    parser.add_argument("--period", required=True, help="Report period YYYY14MM, e.g. 20261407")
    parser.add_argument("--config", default=str(ROOT / "config" / "default.yaml"))
    parser.add_argument("--out", required=True, help="Output CSV path")
    parser.add_argument("--mode", choices=("mom", "yoy"), default="mom")
    args = parser.parse_args()

    df = run_rca(
        input_path=args.input,
        period=args.period,
        config_path=args.config,
        out_path=args.out,
        mode=args.mode,
    )
    print(f"Wrote {len(df)} rows to {args.out}")
    print(f"market_sign={df['market_sign'].iloc[0] if len(df) else 'n/a'} "
          f"overall_delta={df['overall_delta_value'].iloc[0] if len(df) else 'n/a'}")


if __name__ == "__main__":
    main()
