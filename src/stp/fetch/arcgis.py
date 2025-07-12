"""Fetchers for ArcGIS REST services."""

from __future__ import annotations

import functools
from io import BytesIO
import logging
import os
from pathlib import Path
from typing import List, Optional, Tuple

import geopandas as gpd

from stp.core.config import load_config  # YAML loader/merger
from stp.core.http import fetch_bytes  # For retries/timeout
from stp.storage.file_storage import sanitize_layer_name

from ._optional_deps import DATAFRAME_LIKE

__all__ = ["fetch_arcgis_vector", "fetch_arcgis_table", "load_workflow_cached", "get_layer_name"]

logger = logging.getLogger(__name__)


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
    data = fetch_bytes(url)
    gdf = gpd.read_file(BytesIO(data))
    epsg = gdf.crs.to_epsg() or DEFAULT_EPSG
    layer_name = sanitize_layer_name(Path(service_url).stem)
    return [(layer_name, gdf, epsg, 4326)]


def fetch_arcgis_table(
    service_url: str,
) -> List[Tuple[str, gpd.GeoDataFrame, int]]:
    """Fetch a non-spatial table from an ArcGIS service."""
    url = _build_query_url(service_url, as_geojson=True)
    data = fetch_bytes(url)
    gdf = gpd.read_file(BytesIO(data))
    gdf.set_crs(epsg=DEFAULT_EPSG, inplace=True)
    layer_name = sanitize_layer_name(Path(service_url).stem)
    return [(layer_name, gdf, DEFAULT_EPSG)]


_VECTOR_FORMATS = {"shapefile", "geojson", "feature"}  # Expanded


@functools.lru_cache(maxsize=128)
def load_workflow_cached() -> dict:
    """Cached load of workflow.yaml."""
    return load_config("workflow.yaml")


DEFAULT_EPSG = load_workflow_cached().get("default_epsg", 4326)


TTL = int(os.getenv("ARC_LAYER_NAME_TTL", "3600"))
@functools.lru_cache(maxsize=128 if TTL else 0)
def get_layer_name(url: str) -> str:
    """Fetch layer name from service metadata."""
    base_url = url.split("?", 1)[0]  # Strip params for cache stability
    meta_url = f"{base_url}?f=json"
    try:
        data = fetch_json_with_retry(meta_url)  # Use retry helper
        return data.get("name", "unnamed_layer")
    except Exception as exc:
        logger.warning(
            "Failed to fetch layer name from %s: %s", meta_url, exc
        )
        return base_url.split("/")[-2]  # Fallback


def _decide_vector_mode(
    *,
    yaml_has_geometry: bool | None,
    fmt: str,
    runtime_override: bool | None,
) -> bool:
    """
    Return True if we should treat the endpoint as a vector layer.
    Priority: yaml flag > runtime override > format inference.
    """
    if yaml_has_geometry is not None:
        return yaml_has_geometry
    if runtime_override is not None:
        return runtime_override
    return fmt in _VECTOR_FORMATS


def fetch_arcgis(
    source_id: str, is_vector: Optional[bool] = None, **kwargs
) -> List[Tuple[str, DATAFRAME_LIKE, Optional[int]]]:
    """
    Dispatcher for ArcGIS fetches.

    Loads config from workflow.yaml, determines vector/table via
    'has_geometry' (primary), format inference, or is_vector override.
    Delegates to helpers. Helpers should accept filter_query/max_records
    or use **_ guard.

    Parameters
    ----------
    source_id : str
        Source ID from workflow.yaml (e.g., 'sidewalk').
    is_vector : bool, optional
        Runtime override for vector/table.
    **kwargs : dict
        Passed to helpers (e.g., custom params).

    Returns
    -------
    List[Tuple[str, DataFrameLike, Optional[int]]]
        (layer_name, DataFrame/GeoDataFrame/None, src_epsg) tuples.
        src_epsg is None for non-spatial tables.
    """
    wf = load_workflow_cached()
    try:
        src = wf["sources"][source_id]
    except KeyError as exc:
        raise ValueError(f"Unknown source_id '{source_id}'") from exc

    url = src.get("url")
    if not url:
        raise ValueError(f"No URL for '{source_id}' in workflow.yaml")

    fmt = src.get("format", "").lower()
    filter_query = src.get("filter")
    max_records = src.get("limits", {}).get("arcgis_default_max_records", 1000)

    use_vector = _decide_vector_mode(
        yaml_has_geometry=src.get("has_geometry"),
        fmt=fmt,
        runtime_override=is_vector,
    )

    layer_name = get_layer_name(url)

    if use_vector:
        results = fetch_arcgis_vector(
            url,
            filter_query=filter_query,
            max_records=max_records,
            **kwargs,
        )
    else:
        results = fetch_arcgis_table(
            url,
            filter_query=filter_query,
            max_records=max_records,
            **kwargs,
        )
        results = [(n, df, None) for n, df, _ in results]

    rows = sum(len(df) for _, df, _ in results if df is not None)
    logger.info("Fetched %d rows from %s (%s)", rows, source_id, "vector" if use_vector else "table")

    return results