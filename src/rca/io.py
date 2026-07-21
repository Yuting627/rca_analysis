"""CSV I/O helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from rca.schema import map_columns, validate_frame


def read_sku_monthly(path: str | Path, cfg: dict[str, Any]) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = map_columns(df, cfg)
    eps = float(cfg.get("epsilon", 1e-9))
    return validate_frame(df, eps=eps)


def write_output(df: pd.DataFrame, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
