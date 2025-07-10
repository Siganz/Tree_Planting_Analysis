"""Placeholder Socrata fetcher."""

from __future__ import annotations

from typing import List, Tuple, Optional

import geopandas as gpd

__all__ = ["dispatch_socrata_table"]


def dispatch_socrata_table(url: str, app_token: Optional[str] = None
                           ) -> List[Tuple[str, gpd.GeoDataFrame, int]]:
    """Temporary stub for Socrata dataset fetching."""
    raise NotImplementedError("Socrata fetcher not implemented")
