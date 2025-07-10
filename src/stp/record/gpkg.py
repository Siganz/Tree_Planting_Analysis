"""Extract field inventory from a GeoPackage."""

from __future__ import annotations

from pathlib import Path
from typing import List, Dict

import fiona
import pandas as pd

__all__ = ["from_gpkg"]


def from_gpkg(gpkg_path: Path) -> pd.DataFrame:
    """Return field inventory for all layers in *gpkg_path*.

    The returned ``DataFrame`` has columns ``layer_name``, ``field_name`` and
    ``field_type``.
    """
    rows: List[Dict[str, str]] = []
    for layer in fiona.listlayers(str(gpkg_path)):
        with fiona.open(str(gpkg_path), layer=layer) as src:
            for field, ftype in src.schema["properties"].items():
                rows.append(
                    {
                        "layer_name": layer,
                        "field_name": field,
                        "field_type": ftype,
                    }
                )
    return pd.DataFrame(rows)
