import os
import requests
import zipfile
import tempfile
import shutil
from pathlib import Path
from io import BytesIO
import geopandas as gpd
import pandas as pd
import fiona
from shapely.geometry import Point
from storage_helpers import sanitize_layer_name

session = requests.Session()

# ────────────────────────────────────────────────────────────────────────────────
# Socrata helpers
# ────────────────────────────────────────────────────────────────────────────────

def fetch_socrata_table(url: str, app_token: str = None):
    """
    Fetch a Socrata table (JSON) endpoint and return a list of one tuple:
      [(layer_name, GeoDataFrame, source_epsg)].

    This function will attempt to find geometry in the following order:
     1) Columns named "latitude" & "longitude" (assumed EPSG:4326).
     2) A GeoJSON-style "location" field: {"type":"Point","coordinates":[lon,lat]}.
     3) A WKT "geometry" field: "POINT(lon lat)".
     4) Projected X/Y fields (e.g. "sign_x_coord" & "sign_y_coord")—assumed EPSG:2263.

    Returns [] if no geometry can be found.
    """
    headers = {}
    if app_token:
        headers["X-App-Token"] = app_token

    # If this is the hn5i-inap endpoint without a $limit, add one to pull all rows
    if url.lower().endswith(".json") and "resource/hn5i-inap.json" in url.lower():
        if "?" in url:
            url = url + "&$limit=50000"
        else:
            url = url + "?$limit=50000"

    resp = session.get(url, headers=headers)
    resp.raise_for_status()

    data = None
    try:
        data = resp.json()
    except ValueError:
        # If it’s not JSON, try CSV fallback
        # We already have the response content, so parse it directly
        df = pd.read_csv(BytesIO(resp.content))
    else:
        df = pd.DataFrame(data)

    if df.empty:
        return []

    # CASE 1: explicit "latitude" & "longitude"
    if {"latitude", "longitude"}.issubset(df.columns):
        try:
            df["latitude"] = df["latitude"].astype(float)
            df["longitude"] = df["longitude"].astype(float)
            geom = [Point(xy) for xy in zip(df.longitude, df.latitude)]
            gdf = gpd.GeoDataFrame(
                df.drop(columns=["latitude", "longitude"]),
                geometry=geom,
                crs="EPSG:4326"
            )
            layer_name = sanitize_layer_name(Path(url).stem)
            return [(layer_name, gdf, 4326)]
        except Exception:
            pass  # If parsing fails, fall through to next case

    # CASE 2: GeoJSON-style "location" field
    if "location" in df.columns:
        coords = []
        rows = []
        for record in df.to_dict(orient="records"):
            loc = record.get("location")
            if isinstance(loc, dict) and loc.get("type") == "Point":
                try:
                    lon, lat = loc["coordinates"]
                    lon, lat = float(lon), float(lat)
                    coords.append(Point(lon, lat))
                    # Copy everything except "location" into the attribute dict
                    rec_copy = {k: v for k, v in record.items() if k != "location"}
                    rows.append(rec_copy)
                except Exception:
                    continue
        if coords:
            gdf = gpd.GeoDataFrame(rows, geometry=coords, crs="EPSG:4326")
            layer_name = sanitize_layer_name(Path(url).stem)
            return [(layer_name, gdf, 4326)]

    # CASE 3: WKT "geometry" field
    if "geometry" in df.columns:
        coords = []
        rows = []
        for record in df.to_dict(orient="records"):
            wkt = record.get("geometry")
            if isinstance(wkt, str) and wkt.startswith("POINT"):
                try:
                    # e.g. "POINT(-73.8165 40.7162)"
                    inside = wkt[len("POINT(") : -1].split()
                    lon, lat = float(inside[0]), float(inside[1])
                    coords.append(Point(lon, lat))
                    # Copy everything except "geometry"
                    rec_copy = {k: v for k, v in record.items() if k != "geometry"}
                    rows.append(rec_copy)
                except Exception:
                    continue
        if coords:
            gdf = gpd.GeoDataFrame(rows, geometry=coords, crs="EPSG:4326")
            layer_name = sanitize_layer_name(Path(url).stem)
            return [(layer_name, gdf, 4326)]

    # CASE 4: projected X/Y fields (e.g. "sign_x_coord" & "sign_y_coord")
    # Here we assume EPSG:2263 if both fields exist.
    x_field = None
    y_field = None
    # You can customize this to match any pair of fields your tables use.
    if "sign_x_coord" in df.columns and "sign_y_coord" in df.columns:
        x_field, y_field = "sign_x_coord", "sign_y_coord"
        source_epsg = 2263
    # You could add more pairs here if other tables use different column names.

    if x_field and y_field:
        coords = []
        rows = []
        for record in df.to_dict(orient="records"):
            try:
                x = float(record.get(x_field))
                y = float(record.get(y_field))
                coords.append(Point(x, y))
                rec_copy = {k: v for k, v in record.items() if k not in (x_field, y_field)}
                rows.append(rec_copy)
            except Exception:
                continue
        if coords:
            gdf = gpd.GeoDataFrame(rows, geometry=coords, crs=f"EPSG:{source_epsg}")
            layer_name = sanitize_layer_name(Path(url).stem)
            return [(layer_name, gdf, source_epsg)]

    # If we reach here, no geometry was found
    return []

def fetch_socrata_vector(url: str, app_token: str = None):
    """
    Fetch a Socrata “vector” (GeoJSON) endpoint and return a GeoDataFrame in EPSG:4326.
    Request parameters: f=geojson, $limit=50000. Returns:
      [(layer_name, GeoDataFrame, source_epsg=4326)]
    """
    headers = {}
    if app_token:
        headers["X-App-Token"] = app_token

    # If the URL already ends with “.geojson”, just add $limit; otherwise force &f=geojson
    if url.lower().endswith(".geojson"):
        resp = session.get(url, headers=headers, params={"$limit": 50000})
    else:
        resp = session.get(
            url,
            headers=headers,
            params={"$limit": 50000, "f": "geojson"}
        )
    resp.raise_for_status()

    try:
        gdf = gpd.read_file(BytesIO(resp.content))
    except Exception:
        return []

    # GeoPandas might not auto‐assign a CRS, so force WGS84
    gdf.set_crs(epsg=4326, inplace=True)

    layer_name = sanitize_layer_name(Path(url).stem)
    return [(layer_name, gdf, 4326)]

def export_spatial_layer(gdf, data_id, gpkg_path):
    """
    Write gdf to gpkg_path as layer=data_id.
    """
    gdf.to_file(gpkg_path, layer=data_id, driver="GPKG")

# ────────────────────────────────────────────────────────────────────────────────
# ArcGIS helpers
# ────────────────────────────────────────────────────────────────────────────────

def fetch_arcgis_table(url: str):
    """
    Fetch an ArcGIS REST “table” endpoint as JSON → GeoDataFrame with EPSG:4326.
    If no lat/long fields exist, returns []. Otherwise returns:
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
        crs="EPSG:4326"
    )
    layer_name = sanitize_layer_name(Path(url).stem)
    return [(layer_name, gdf, 4326)]

def fetch_arcgis_vector(url: str):
    """
    Fetch an ArcGIS FeatureServer “vector” endpoint in pages, so you get ALL features.
    1) GET <url>?f=json to read service metadata (esp. maxRecordCount, WKID).
    2) Loop over resultOffset in increments of maxRecordCount, pulling GeoJSON each time.
    3) Concatenate all pages into one GeoDataFrame (in EPSG:4326).
    Returns [(None, gdf_all, 4326, native_wkid)].
    The main loop will substitute layer_id and record native_wkid.
    """
    # 1) Read service metadata & extract WKID + maxRecordCount
    info = session.get(f"{url}?f=json").json()
    sr = info.get("spatialReference", {})
    native_wkid = sr.get("latestWkid") or sr.get("wkid") or 4326

    max_records = info.get("maxRecordCount", 1000)
    if not isinstance(max_records, int) or max_records < 1:
        max_records = 1000  # fallback if the service returns something unexpected

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

        # Force CRS to WGS84 (GeoJSON is always in 4326)
        page_gdf = page_gdf.set_crs(epsg=4326, allow_override=True)

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
        #drop columns that are NA 
        df = df.dropna(axis=1, how="all")
        clean_parts.append(df)

    gdf_full = gpd.GeoDataFrame(
        pd.concat(clean_parts, ignore_index=True),
        crs="EPSG:4326"
    )

    return [(None, gdf_full, 4326, native_wkid)]

# ────────────────────────────────────────────────────────────────────────────────
# “Direct” helpers (no Socrata/ArcGIS)
# ────────────────────────────────────────────────────────────────────────────────

def fetch_geojson_direct(url: str):
    """
    Download a raw GeoJSON URL and return (layer_name, GeoDataFrame, source_epsg=4326).
    """
    resp = session.get(url)
    resp.raise_for_status()

    try:
        gdf = gpd.read_file(BytesIO(resp.content))
    except Exception:
        return []

    gdf.set_crs(epsg=4326, inplace=True)
    layer_name = sanitize_layer_name(Path(url).stem)
    return [(layer_name, gdf, 4326)]

def fetch_csv_direct(url: str):
    """
    Download a raw CSV URL and return (layer_name, GeoDataFrame, source_epsg=4326)
    if it has latitude/longitude columns, else [].
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
    Download a GeoPackage from a URL, read each layer into a GeoDataFrame, and
    return [(layer_name, gdf, source_epsg)]. If no CRS is stored, assume 4326.
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
            gdf.set_crs(epsg=4326, inplace=True)

        results.append((ln, gdf, 4326))

    return results

def fetch_gdb_or_zip(url: str):
    """
    Download a zipped FileGDB or Shapefile URL, extract locally, read each dataset
    into GeoDataFrames, and return [(layer_name, gdf, source_epsg=4326)]. If no CRS,
    assume 4326. Cleans up temp files on exit.
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
    gdb_candidates = [p for p in Path(temp_root).iterdir() if p.suffix.lower() == ".gdb"]
    if gdb_candidates:
        # Read each layer in the first FileGDB found
        gdb_path = gdb_candidates[0]
        for ln in fiona.listlayers(str(gdb_path)):
            gdf = gpd.read_file(str(gdb_path), layer=ln)
            if gdf.empty:
                continue
            if gdf.crs is None:
                gdf.set_crs(epsg=4326, inplace=True)
            results.append((ln, gdf, 4326))
    else:
        # Treat all Shapefile (.shp) files under temp_root
        for shp in Path(temp_root).rglob("*.shp"):
            gdf = gpd.read_file(str(shp))
            if gdf.empty:
                continue
            if gdf.crs is None:
                gdf.set_crs(epsg=4326, inplace=True)
            layer_name = shp.stem
            results.append((layer_name, gdf, 4326))

    shutil.rmtree(temp_root)
    return results
