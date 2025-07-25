"""
Fetcher utilization
"""
# src/stp/scripts/download_utils.py

from stp.fetch.socrata import dispatch_socrata_table
from stp.fetch.arcgis import fetch_arcgis_table, fetch_arcgis_vector
from stp.fetch.csv import fetch_csv_direct
from stp.fetch.geojson import fetch_geojson_direct
from stp.fetch.gdb import fetch_gdb_or_zip
from stp.fetch.gpkg import fetch_gpkg_layers

FETCHERS = {
    ("socrata", "csv"):   dispatch_socrata_table,
    ("socrata", "json"):  dispatch_socrata_table,
    ("socrata", "geojson"): dispatch_socrata_table,
    ("socrata", "shapefile"): dispatch_socrata_table,
    ("arcgis", "csv"):    fetch_arcgis_table,
    ("arcgis", "json"):   fetch_arcgis_table,
    ("arcgis", "geojson"): fetch_arcgis_vector,
    ("arcgis", "shapefile"): fetch_arcgis_vector,
    (None, "csv"):        fetch_csv_direct,
    (None, "geojson"):    fetch_geojson_direct,
    (None, "shapefile"):  fetch_gdb_or_zip,
    (None, "gpkg"):       fetch_gpkg_layers,
}
