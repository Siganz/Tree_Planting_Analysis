"""Fetch layers from a GeoPackage."""

from __future__ import annotations

from pathlib import Path
from typing import List, Tuple
from tempfile import TemporaryDirectory

import fiona
import geopandas as gpd

from .. import http_client
from ..storage.file_storage import sanitize_layer_name
from ..settings import DEFAULT_EPSG

__all__ = ["fetch_gpkg_layers"]


def fetch_gpkg_layers(
    path_or_url: str,
) -> List[Tuple[str, gpd.GeoDataFrame, int]]:
    """Load all layers from a GeoPackage file or URL."""
    tmpdir: TemporaryDirectory | None = None
    gpkg_path = Path(path_or_url)
    if path_or_url.startswith("http"):
        tmpdir = TemporaryDirectory()
        gpkg_path = Path(tmpdir.name) / "data.gpkg"
        gpkg_path.write_bytes(http_client.fetch_bytes(path_or_url))
    try:
        results: List[Tuple[str, gpd.GeoDataFrame, int]] = []
        for layer in fiona.listlayers(str(gpkg_path)):
            gdf = gpd.read_file(gpkg_path, layer=layer)
            epsg = gdf.crs.to_epsg() or DEFAULT_EPSG
            results.append((sanitize_layer_name(layer), gdf, epsg))
        return results
    finally:
        if tmpdir is not None:
            tmpdir.cleanup()
