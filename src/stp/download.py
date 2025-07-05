"""
download.py — Unified fetchers for spatial datasets

This module provides functions to fetch and normalize spatial data
from various sources into GeoDataFrames (always in EPSG:4326 unless
otherwise specified). Supported sources:

  • Socrata tables (JSON or CSV fallback), with point geometry auto‐detection
  • Socrata GeoJSON “vector” endpoints (if needed)
  • ArcGIS REST tables & feature layers (paged geoJSON)
  • Direct GeoJSON, CSV, GeoPackage, zipped FileGDB/Shapefile URLs

Each fetcher returns a list of tuples:
    (layer_name: str, gdf: GeoDataFrame, source_epsg: int[, native_wkid: int])

Helpers:
  • dispatch_socrata_table
  • make_gdf_from_latlon
  • make_gdf_from_geojson_field
  • make_gdf_from_wkt
  • make_gdf_from_projected
  • fetch_socrata_vector
  • fetch_arcgis_table
  • fetch_arcgis_vector
  • fetch_geojson_direct
  • fetch_csv_direct
  • fetch_gpkg_layers
  • fetch_gdb_or_zip
"""


import shutil
import tempfile
from venv import logger
import zipfile
from io import BytesIO
from pathlib import Path
from typing import Optional

import fiona
import geopandas as gpd
import pandas as pd
import requests

from shapely.geometry import Point
from fiona.errors import DriverError, FionaValueError
from pandas.errors import ParserError

from .settings import get_setting
from .storage import sanitize_layer_name

DEFAULT_EPSG = get_setting('default_epsg')
NYSP_EPSG = get_setting('nysp_epsg')
SOCRATA_LIMIT = get_setting('socrata_limit')
ARCGIS_DEFAULT_MAX_RECORDS = get_setting(
    'arcgis_default_max_records'
    )

session = requests.Session()


def fetch_layer(
    url: str,
    source_type: Optional[str],
    fmt: str,
    socrata_token: Optional[str] = None
) -> list[tuple]:
    """
    Dispatch to the correct fetcher based on source_type and fmt.

    Args:
      url: endpoint URL or file path
      source_type: 'socrata', 'arcgis', or None
      fmt: 'csv', 'json', 'geojson', 'shapefile', or 'gpkg'
      socrata_token: only used when source_type == 'socrata'

    Returns:
      list of tuples (raw_name, gdf, source_epsg, service_wkid)
    """
    # map (stype, fmt) → fetch fn
    # inside helpers/download.py (or wherever you keep your FETCHERS)
    fetchers = {
        # everything Socrata → fetch_socrata_table
        ('socrata', 'csv'): fetch_socrata_table,
        ('socrata', 'json'): fetch_socrata_table,
        ('socrata', 'geojson'): fetch_socrata_table,
        ('socrata', 'shapefile'): fetch_socrata_table,

        # ArcGIS stays the same
        ('arcgis', 'csv'): fetch_arcgis_table,
        ('arcgis', 'json'): fetch_arcgis_table,
        ('arcgis', 'geojson'): fetch_arcgis_vector,
        ('arcgis', 'shapefile'): fetch_arcgis_vector,

        # direct‐URL sources
        (None, 'csv'): fetch_csv_direct,
        (None, 'geojson'): fetch_geojson_direct,
        (None, 'shapefile'): fetch_gdb_or_zip,
        (None, 'gpkg'): fetch_gpkg_layers,
    }

    key = (source_type, fmt)
    fn = fetchers.get(key)
    if not fn:
        # split the f-string into two shorter literals
        raise ValueError(
            f"No fetcher for source_type={source_type!r}, "
            f"fmt={fmt!r}")

    # call with the right signature
    if source_type == 'socrata':
        raw = fn(url, app_token=socrata_token)
        # unify to four‐tuple
        return [(n, g, eps, None) for n, g, eps in raw]

    if source_type == 'arcgis':
        raw = fn(url)  # e.g. [(None, gdf, epsg, wkid), ...]
        return raw  # leave the None values intact

    # direct fetchers all return (layer_name, gdf, epsg)
    raw = fn(url)
    return [(n, g, eps, None) for n, g, eps in raw]

# ─────────────────────────────────────────────────────────────────────────────
# Socrata helpers
# ─────────────────────────────────────────────────────────────────────────────


def fetch_socrata_table(url: str, app_token: str = None):
    """Download a Socrata table endpoint and return any point geometry.

    The function attempts, in order:
    1. 'latitude'/'longitude' columns.
    2. GeoJSON-style 'location' dict.
    3. WKT 'geometry' string.
    4. Projected X/Y columns.

    Args:
        url (str): URL to a Socrata table endpoint.
        app_token (str, optional): Socrata App Token.

    Returns:
        list[tuple]: [(layer_name, GeoDataFrame, source_epsg)]
        or [] if no valid points.
    """
    headers = {'X-App-Token': app_token} if app_token else {}
    if (
        url.lower().endswith('.json')
        and 'resource/hn5i-inap.json' in url.lower()
    ):
        join_char = '&' if '?' in url else '?'
        url = f'{url}{join_char}$limit={SOCRATA_LIMIT}'
    resp = session.get(url, headers=headers)
    resp.raise_for_status()
    try:
        data = resp.json()
        df = pd.DataFrame(data)
    except ValueError:
        df = pd.read_csv(BytesIO(resp.content))
    if df.empty:
        return []
    layer_name = sanitize_layer_name(Path(url).stem)
    if {'latitude', 'longitude'}.issubset(df.columns):
        return make_gdf_from_latlon(df, layer_name)
    if 'location' in df.columns:
        return make_gdf_from_geojson_field(df, layer_name)
    if 'geometry' in df.columns:
        return make_gdf_from_wkt(df, layer_name)
    if {'sign_x_coord', 'sign_y_coord'}.issubset(df.columns):
        return make_gdf_from_projected(
            df,
            layer_name,
            'sign_x_coord',
            'sign_y_coord',
            NYSP_EPSG,
        )
    return []


def make_gdf_from_latlon(df, layer_name):
    """Build a GeoDataFrame from 'latitude' & 'longitude' columns.

    Args:
        df (pd.DataFrame): DataFrame with 'latitude' and 'longitude'.
        layer_name (str): Sanitized layer name for metadata.

    Returns:
        list[tuple]: [(layer_name, GeoDataFrame, DEFAULT_EPSG)]
        or [] if conversion fails.
    """
    try:
        df['latitude'] = df['latitude'].astype(float)
        df['longitude'] = df['longitude'].astype(float)
        pts = gpd.points_from_xy(df.longitude, df.latitude)
        gdf = gpd.GeoDataFrame(
            df.drop(columns=['latitude', 'longitude']),
            geometry=pts,
            crs=f'EPSG:{DEFAULT_EPSG}',
        )
        return [(layer_name, gdf, DEFAULT_EPSG)]
    except (ValueError, TypeError):
        return []


def make_gdf_from_geojson_field(df, layer_name):
    """Build a GeoDataFrame from a GeoJSON-style 'location' field.

    Args:
        df (pd.DataFrame): DataFrame with a 'location' column.
        layer_name (str): Sanitized layer name for metadata.

    Returns:
        list[tuple]: [(layer_name, GeoDataFrame, DEFAULT_EPSG)]
        or [] if no valid points.
    """
    coords = []
    rows = []
    for rec in df.to_dict(orient='records'):
        loc = rec.get('location')
        if isinstance(loc, dict) and loc.get('type') == 'Point':
            try:
                lon, lat = map(float, loc['coordinates'])
            except (ValueError, TypeError):
                continue
            coords.append(Point(lon, lat))
            rows.append({k: v for k, v in rec.items() if k != 'location'})
    if coords:
        gdf = gpd.GeoDataFrame(rows, geometry=coords,
                               crs=f'EPSG:{DEFAULT_EPSG}')
        return [(layer_name, gdf, DEFAULT_EPSG)]
    return []


def make_gdf_from_wkt(df, layer_name):
    """Build a GeoDataFrame from a WKT 'geometry' text field.

    Args:
        df (pd.DataFrame): DataFrame with a 'geometry' column.
        layer_name (str): Sanitized layer name for metadata.

    Returns:
        list[tuple]: [(layer_name, GeoDataFrame, DEFAULT_EPSG)]
        or [] if no valid points.
    """
    coords = []
    rows = []
    for rec in df.to_dict(orient='records'):
        wkt = rec.get('geometry')
        if isinstance(wkt, str) and wkt.startswith('POINT'):
            try:
                lon, lat = map(float, wkt[len('POINT('):-1].split())
            except (ValueError, TypeError):
                continue
            coords.append(Point(lon, lat))
            rows.append({k: v for k, v in rec.items()
                         if k != 'geometry'})
    if coords:
        gdf = gpd.GeoDataFrame(rows, geometry=coords,
                               crs=f'EPSG:{DEFAULT_EPSG}')
        return [(layer_name, gdf, DEFAULT_EPSG)]
    return []


def make_gdf_from_projected(df, layer_name, x_col, y_col, epsg):
    """Build a GeoDataFrame from projected X/Y coordinate columns.

    Args:
        df (pd.DataFrame): DataFrame with x_col and y_col fields.
        layer_name (str): Sanitized layer name for metadata.
        x_col (str): Name of the easting field.
        y_col (str): Name of the northing field.
        epsg (int): EPSG code of the projected CRS.

    Returns:
        list[tuple]: [(layer_name, GeoDataFrame, epsg)]
        or [] if no valid points.
    """
    coords = []
    rows = []
    for rec in df.to_dict(orient='records'):
        try:
            x = float(rec.get(x_col))
            y = float(rec.get(y_col))
        except (ValueError, TypeError):
            continue
        coords.append(Point(x, y))
        rows.append({k: v for k, v in rec.items()
                     if k not in (x_col, y_col)})
    if coords:
        gdf = gpd.GeoDataFrame(rows, geometry=coords,
                               crs=f'EPSG:{epsg}')
        return [(layer_name, gdf, epsg)]
    return []

# ─────────────────────────────────────────────────────────────────────────────
# ArcGIS helpers
# ─────────────────────────────────────────────────────────────────────────────


def fetch_arcgis_table(url: str):
    """
    Fetch an ArcGIS REST "table" endpoint as JSON and return a GeoDataFrame
    in EPSG:4326. If no latitude/longitude fields exist, returns [].

    Returns:
      [(layer_name, GeoDataFrame, source_epsg=4326)].
    """
    query_url = f"{url}/query?where=1=1&outFields=*&f=json"
    resp = session.get(query_url)
    resp.raise_for_status()

    features = resp.json().get("features", [])
    if not features:
        return []

    rows = [feat.get("attributes", {}) for feat in features]
    df = pd.DataFrame(rows)
    if "latitude" not in df.columns or "longitude" not in df.columns:
        return []

    geometry = [Point(xy) for xy in zip(df.longitude, df.latitude)]
    gdf = gpd.GeoDataFrame(
        df.drop(columns=["latitude", "longitude"]),
        geometry=geometry,
        crs=f"EPSG:{DEFAULT_EPSG}"
    )
    layer_name = sanitize_layer_name(Path(url).stem)
    return [(layer_name, gdf, DEFAULT_EPSG)]


def fetch_arcgis_vector(
        url: str
) -> list[tuple[str, gpd.GeoDataFrame, int, int]]:
    """
    Fetch all features from an ArcGIS FeatureServer vector endpoint.

    Pages through the service using `resultOffset` until no more features
    are returned. Always returns a single GeoDataFrame in EPSG:4326.

    Args:
        url (str): Base URL of the ArcGIS FeatureServer layer
                   (e.g. 'https://.../FeatureServer/0').

    Returns:
        List of one tuple:
          [
            (None, GeoDataFrame(all_features), DEFAULT_EPSG, native_wkid)
          ]
        or [] if no valid pages are found.
    """
    # 1) Read service metadata
    info = session.get(f"{url}?f=json").json()
    sr = info.get("spatialReference", {})
    native_wkid = sr.get("latestWkid") or sr.get("wkid") or DEFAULT_EPSG

    max_records = info.get("maxRecordCount", ARCGIS_DEFAULT_MAX_RECORDS)
    if not isinstance(max_records, int) or max_records < 1:
        max_records = ARCGIS_DEFAULT_MAX_RECORDS

    # 2) Page through all features
    parts: list[gpd.GeoDataFrame] = []
    offset = 0
    while True:
        params = {
            "where": "1=1",
            "outFields": "*",
            "f": "pgeojson",
            "resultOffset": offset,
            "resultRecordCount": max_records,
        }
        resp = session.get(f"{url}/query", params=params)
        resp.raise_for_status()

        try:
            page_gdf = gpd.read_file(BytesIO(resp.content))
        except (fiona.errors.DriverError, ValueError):
            break

        if page_gdf.empty:
            break

        # Ensure correct CRS
        page_gdf = page_gdf.set_crs(epsg=DEFAULT_EPSG, allow_override=True)
        parts.append(page_gdf)
        offset += max_records

    if not parts:
        return []

    # 3) Concatenate and clean empty columns
    full = pd.concat(parts, ignore_index=True)
    # drop columns that are entirely NaN
    full = full.dropna(axis=1, how="all")
    gdf_all = gpd.GeoDataFrame(full, crs=f"EPSG:{DEFAULT_EPSG}")

    return [(None, gdf_all, DEFAULT_EPSG, native_wkid)]


# ─────────────────────────────────────────────────────────────────────────────
# "Direct" helpers (no Socrata/ArcGIS)
# ─────────────────────────────────────────────────────────────────────────────


def fetch_geojson_direct(url: str):
    """
    Download a raw GeoJSON URL and return a list of tuples:
      (layer_name, GeoDataFrame, source_epsg=4326).
    """
    resp = session.get(url)
    resp.raise_for_status()
    try:
        gdf = gpd.read_file(BytesIO(resp.content))
    except (FionaValueError, DriverError) as err:
        logger.warning("GeoJSON read failed for %s: %s", url, err)
        return []

    gdf.set_crs(epsg=DEFAULT_EPSG, inplace=True)
    layer_name = sanitize_layer_name(Path(url).stem)
    return [(layer_name, gdf, DEFAULT_EPSG)]


def fetch_csv_direct(url: str):
    """
    Download a raw CSV URL and return a list of tuples:
      (layer_name, GeoDataFrame, source_epsg=4326) if it has latitude/
      longitude columns; else [].
    """
    resp = session.get(url)
    resp.raise_for_status()
    try:
        df = pd.read_csv(BytesIO(resp.content))
    except ParserError as err:
        logger.warning("CSV parse failed for %s: %s", url, err)
        return []

    if "latitude" not in df.columns or "longitude" not in df.columns:
        return []

    geometry = [Point(xy) for xy in zip(df.longitude, df.latitude)]
    gdf = gpd.GeoDataFrame(
        df.drop(columns=["latitude", "longitude"]),
        geometry=geometry,
        crs="EPSG:4326",
    )
    layer_name = sanitize_layer_name(Path(url).stem)
    return [(layer_name, gdf, 4326)]


def fetch_gpkg_layers(url: str):
    """
    Download a GeoPackage from a URL and read each layer into a GeoDataFrame.
    Return [(layer_name, gdf, source_epsg)]. If no CRS is stored, assume 4326.
    """
    resp = session.get(url, stream=True)
    resp.raise_for_status()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".gpkg") as tmp:
        for chunk in resp.iter_content(chunk_size=4096):
            tmp.write(chunk)
        gpkg_path = Path(tmp.name)

    results = []
    for ln in fiona.listlayers(str(gpkg_path)):
        gdf = gpd.read_file(str(gpkg_path), layer=ln)
        if gdf.empty:
            continue

        if gdf.crs is None:
            gdf.set_crs(epsg=DEFAULT_EPSG, inplace=True)

        results.append((ln, gdf, DEFAULT_EPSG))

    return results


def fetch_gdb_or_zip(url: str):
    """
    Download a zipped FileGDB or Shapefile URL, extract locally, and read each
    dataset into GeoDataFrames. Return [(layer_name, gdf, source_epsg=4326)].
    If no CRS is found, assume 4326. Cleans up temp files on exit.
    """
    resp = session.get(url)
    resp.raise_for_status()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
        tmp.write(resp.content)
        zip_path = Path(tmp.name)

    temp_root = tempfile.mkdtemp()
    results = []

    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(temp_root)

    # Check for FileGDB folders (*.gdb)
    gdb_candidates = [
        p
        for p in Path(temp_root).iterdir()
        if p.suffix.lower() == ".gdb"
    ]
    if gdb_candidates:
        # Read each layer in the first FileGDB found
        gdb_path = gdb_candidates[0]
        for ln in fiona.listlayers(str(gdb_path)):
            gdf = gpd.read_file(str(gdb_path), layer=ln)
            if gdf.empty:
                continue
            if gdf.crs is None:
                gdf.set_crs(epsg=DEFAULT_EPSG, inplace=True)
            results.append((ln, gdf, DEFAULT_EPSG))
    else:
        # Treat all Shapefile (.shp) files under temp_root
        for shp in Path(temp_root).rglob("*.shp"):
            gdf = gpd.read_file(str(shp))
            if gdf.empty:
                continue
            if gdf.crs is None:
                gdf.set_crs(epsg=DEFAULT_EPSG, inplace=True)
            layer_name = shp.stem
            results.append((layer_name, gdf, DEFAULT_EPSG))

    shutil.rmtree(temp_root)
    return results
