"""Fetchers for ArcGIS REST services."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import List, Tuple

import geopandas as gpd

from .. import http_client
from ..storrage.file_storage import sanitize_layer_name
from ..settings import DEFAULT_EPSG

__all__ = ["fetch_arcgis_vector", "fetch_arcgis_table"]


def _build_query_url(service_url: str, as_geojson: bool = True) -> str:
    """Return an ArcGIS REST query URL for *service_url*."""
    base = service_url.rstrip("/")
    if not base.lower().endswith("query"):
        base = f"{base}/query"
    params = "where=1%%3D1&outFields=*&returnGeometry=true"
    if as_geojson:
        params += "&outSR=4326&f=geojson"
    else:
        params += "&f=json"
    return f"{base}?{params}"


def fetch_arcgis_vector(
    service_url: str,
) -> List[Tuple[str, gpd.GeoDataFrame, int, int]]:
    """Fetch vector data from an ArcGIS FeatureServer layer."""
    url = _build_query_url(service_url, as_geojson=True)
    data = http_client.fetch_bytes(url)
    gdf = gpd.read_file(BytesIO(data))
    epsg = gdf.crs.to_epsg() or DEFAULT_EPSG
    layer_name = sanitize_layer_name(Path(service_url).stem)
    return [(layer_name, gdf, epsg, 4326)]


def fetch_arcgis_table(
    service_url: str,
) -> List[Tuple[str, gpd.GeoDataFrame, int]]:
    """Fetch a non-spatial table from an ArcGIS service."""
    url = _build_query_url(service_url, as_geojson=True)
    data = http_client.fetch_bytes(url)
    gdf = gpd.read_file(BytesIO(data))
    gdf.set_crs(epsg=DEFAULT_EPSG, inplace=True)
    layer_name = sanitize_layer_name(Path(service_url).stem)
    return [(layer_name, gdf, DEFAULT_EPSG)]
