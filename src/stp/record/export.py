"""Export inventory DataFrames."""

from __future__ import annotations

from pathlib import Path
import pandas as pd

__all__ = ["to_csv"]


def to_csv(df: pd.DataFrame, out_csv: Path, show_path: bool = True) -> None:
    """Write *df* to *out_csv* and optionally print the path."""
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv, index=False)
    if show_path:
        print(f"Schema inventory written to {out_csv}")
