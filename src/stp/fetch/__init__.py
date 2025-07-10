"""Spatial data fetcher helpers."""

from .csv import fetch_csv_direct
from .geojson import fetch_geojson_direct
from .arcgis import fetch_arcgis_vector, fetch_arcgis_table
from .gdb import fetch_gdb_or_zip
from .gpkg import fetch_gpkg_layers
from .socrata import dispatch_socrata_table

__all__ = [
    "fetch_csv_direct",
    "fetch_geojson_direct",
    "fetch_arcgis_vector",
    "fetch_arcgis_table",
    "fetch_gdb_or_zip",
    "fetch_gpkg_layers",
    "dispatch_socrata_table",
]
