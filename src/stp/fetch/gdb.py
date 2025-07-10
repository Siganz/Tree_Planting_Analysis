"""Fetchers for zipped shapefiles or geodatabases."""

from __future__ import annotations

from pathlib import Path
from typing import List, Tuple
from tempfile import TemporaryDirectory
import zipfile

import fiona
import geopandas as gpd

from .. import http_client
from ..storage.file_storage import sanitize_layer_name
from ..settings import DEFAULT_EPSG

__all__ = ["fetch_gdb_or_zip"]


def fetch_gdb_or_zip(url: str) -> List[Tuple[str, gpd.GeoDataFrame, int]]:
    """Download a zipped archive and extract layers."""
    data = http_client.fetch_bytes(url)
    results: List[Tuple[str, gpd.GeoDataFrame, int]] = []
    with TemporaryDirectory() as tmpdir:
        zip_path = Path(tmpdir) / "data.zip"
        with open(zip_path, "wb") as fh:
            fh.write(data)
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(tmpdir)
        for shp in Path(tmpdir).rglob("*.shp"):
            gdf = gpd.read_file(shp)
            epsg = gdf.crs.to_epsg() or DEFAULT_EPSG
            results.append((sanitize_layer_name(shp.stem), gdf, epsg))
        for gdb in Path(tmpdir).rglob("*.gdb"):
            for layer in fiona.listlayers(str(gdb)):
                gdf = gpd.read_file(gdb, layer=layer)
                epsg = gdf.crs.to_epsg() or DEFAULT_EPSG
                results.append((sanitize_layer_name(layer), gdf, epsg))
    return results
