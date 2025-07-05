"""Helper constants for download scripts."""

from __future__ import annotations

from ..fetchers import (
    fetch_arcgis_table,
    fetch_arcgis_vector,
    fetch_csv_direct,
    fetch_gdb_or_zip,
    fetch_geojson_direct,
    fetch_gpkg_layers,
    dispatch_socrata_table,
)

FETCHERS = {
    ("socrata", "csv"): dispatch_socrata_table,
    ("socrata", "json"): dispatch_socrata_table,
    ("socrata", "geojson"): dispatch_socrata_table,
    ("socrata", "shapefile"): dispatch_socrata_table,
    ("arcgis", "csv"): fetch_arcgis_table,
    ("arcgis", "json"): fetch_arcgis_table,
    ("arcgis", "geojson"): fetch_arcgis_vector,
    ("arcgis", "shapefile"): fetch_arcgis_vector,
    (None, "csv"): fetch_csv_direct,
    (None, "geojson"): fetch_geojson_direct,
    (None, "shapefile"): fetch_gdb_or_zip,
    (None, "gpkg"): fetch_gpkg_layers,
}
