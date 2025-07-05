"""
download.py

This module provides a unified interface for downloading,
parsing, and convertingspatial datasets into GeoDataFrames.
It supports multiple source formats including:

- Socrata API endpoints (both table and vector formats)
- ArcGIS REST services (tables and paged feature layers)
- Direct GeoJSON, CSV, GPKG, and zipped FileGDB/Shapefile URLs

All returned data is normalized to use EPSG:4326 unless otherwise specified.
Each fetch function returns a list of standardized tuples:
    (layer_name, GeoDataFrame, source_epsg[, native_wkid])

Common use cases include:
- Preprocessing open spatial data
- Pulling geodata from public endpoints (NYC Open Data, ArcGIS, etc.)
- Converting multi-layer sources into consistent GeoDataFrames

Constants like default EPSG codes and record limits are injected from a
`constants.yaml` file via the `get_constant()` helper.

Dependencies: geopandas, pandas, shapely, requests, fiona
"""

import shutil
import tempfile
import zipfile
from io import BytesIO
from pathlib import Path
from typing import Optional

import fiona
import geopandas as gpd
import pandas as pd
import requests
from .config import get_setting
from shapely.geometry import Point
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
        # everything Socrata → dispatch_socrata_table
        ('socrata', 'csv'): dispatch_socrata_table,
        ('socrata', 'json'): dispatch_socrata_table,
        ('socrata', 'geojson'): dispatch_socrata_table,
        ('socrata', 'shapefile'): dispatch_socrata_table,

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
        raise ValueError(f"No fetcher for source_type={source_type!r}, fmt={fmt!r}")

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


def dispatch_socrata_table(url: str, app_token: str = None):
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


def fetch_arcgis_vector(url: str):
    """
    Fetch an ArcGIS FeatureServer "vector" endpoint in pages and return all
    features.

    Steps:
      1) GET <url>?f=json to read service metadata
         (esp. maxRecordCount, WKID).
      2) Loop over resultOffset in increments of maxRecordCount,
         pulling GeoJSON each time.
      3) Concatenate all pages into one GeoDataFrame (in EPSG:4326).

    Returns:
      [(None, gdf_all, 4326, native_wkid)].
    """
    # 1) Read service metadata & extract WKID + maxRecordCount
    info = session.get(f"{url}?f=json").json()
    sr = info.get("spatialReference", {})
    native_wkid = sr.get("latestWkid") or sr.get("wkid") or DEFAULT_EPSG

    max_records = info.get("maxRecordCount", ARCGIS_DEFAULT_MAX_RECORDS)
    if not isinstance(max_records, int) or max_records < 1:
        # fallback if service misbehaves
        max_records = ARCGIS_DEFAULT_MAX_RECORDS

    # 2) Page through all features using resultOffset/resultRecordCount
    all_parts = []  # list of GeoDataFrames for each page
    offset = 0

    while True:
        params = {
            "where": "1=1",
            "outFields": "*",
            "f": "pgeojson",
            "resultOffset": offset,
            "resultRecordCount": max_records
        }
        resp = session.get(f"{url}/query", params=params)
        resp.raise_for_status()

        # Read just this page into a GeoDataFrame
        try:
            page_gdf = gpd.read_file(BytesIO(resp.content))
        except Exception:
            # If the response isn’t valid GeoJSON, stop paging
            break

        if page_gdf.empty:
            # No features left in this page: we’re done
            break

        # Force CRS to WGS84 (GeoJSON is always in DEFAULT_EPSG)
        page_gdf = page_gdf.set_crs(epsg=DEFAULT_EPSG, allow_override=True)

        all_parts.append(page_gdf)

        # Advance the offset
        offset += max_records

    if not all_parts:
        return []

    # 3) Drop empty frames and concatenate all pages into a single GeoDataFrame
    clean_parts = []
    for df in all_parts:
        if df.empty:
            continue
        # drop columns that are NA
        df = df.dropna(axis=1, how="all")
        clean_parts.append(df)

    gdf_full = gpd.GeoDataFrame(
        pd.concat(clean_parts, ignore_index=True),
        crs=f"EPSG:{DEFAULT_EPSG}"
    )

    return [(None, gdf_full, DEFAULT_EPSG, native_wkid)]

# ─────────────────────────────────────────────────────────────────────────────
# "Direct" helpers (no Socrata/ArcGIS)
# ─────────────────────────────────────────────────────────────────────────────


def fetch_geojson_direct(url: str):
    """
    Download a raw GeoJSON URL and return a tuple:
      (layer_name, GeoDataFrame, source_epsg=4326).
    """
    resp = session.get(url)
    resp.raise_for_status()
    try:
        gdf = gpd.read_file(BytesIO(resp.content))
    except Exception:
        return []

    gdf.set_crs(epsg=DEFAULT_EPSG, inplace=True)
    layer_name = sanitize_layer_name(Path(url).stem)
    return [(layer_name, gdf, DEFAULT_EPSG)]


def fetch_csv_direct(url: str):
    """
    Download a raw CSV URL and return a tuple
    (layer_name, GeoDataFrame, source_epsg=4326) if it has latitude/
    longitude columns, else [].
    """
    resp = session.get(url)
    resp.raise_for_status()

    df = pd.read_csv(BytesIO(resp.content))
    if "latitude" not in df.columns or "longitude" not in df.columns:
        return []

    geometry = [Point(xy) for xy in zip(df.longitude, df.latitude)]
    gdf = gpd.GeoDataFrame(
        df.drop(columns=["latitude", "longitude"]),
        geometry=geometry,
        crs="EPSG:4326"
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
