"""Dispatcher for direct dataset downloads."""

from typing import List, Tuple

import geopandas as gpd

from .geojson import fetch_geojson_direct
from .csv import fetch_csv_direct


def fetch_direct(url: str) -> List[Tuple[str, gpd.GeoDataFrame, int]]:
    """Fetch data from *url* using the appropriate fetcher."""
    lower = url.lower()
    if lower.endswith((".geojson", ".json")):
        return fetch_geojson_direct(url)
    if lower.endswith(".csv"):
        return fetch_csv_direct(url)
    raise ValueError(f"Unsupported format: {url}")
