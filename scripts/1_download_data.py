from pathlib import Path
from io import BytesIO
from sqlalchemy import create_engine
from shapely.geometry import Point
import zipfile
import json
import yaml
import requests
import geopandas as gpd
import fiona
import shutil

# 1) Paths
base_dir           = Path.cwd()
config_path        = base_dir / "config" / "config.yaml"
data_sources_path  = base_dir / "config" / "data_sources.json"

# 2) Load config
with open(config_path) as f:
    config = yaml.safe_load(f)

# 3) Setup output folder
output_epsg = config.get("output_epsg", 2263)
output_dir  = Path(config.get("output_dir", "Data/shapefiles"))
output_dir.mkdir(parents=True, exist_ok=True)

# 3.5) DB config & engine
db = config.get("db", {})
if db.get("enabled"):
    conn_url = (
        f"{db['driver']}://{db['user']}:{db['password']}@"
        f"{db['host']}:{db['port']}/{db['database']}"
    )
    engine = create_engine(conn_url)
    print(f"🔗 Connected to PostGIS DB `{db['database']}`")
else:
    print("🔌 Database disabled — writing to files only")
    engine = None

# 3.6) Load layers
with open(data_sources_path, "r") as f:
    layers = json.load(f)

# 4) Session for HTTP
session = requests.Session()

# 5) Helper: get CRS from REST service
def get_layer_crs(rest_url):
    metadata_url = f"{rest_url}?f=json"
    resp = session.get(metadata_url)
    resp.raise_for_status()
    data = resp.json()
    sr = data.get("extent", {}).get("spatialReference", {})
    epsg = sr.get("latestWkid") or sr.get("wkid")
    return int(epsg) if epsg else 4326

# 6) Helper: ArcGIS Services → Shapefile
def fetch_service_layer(rest_url, target_epsg):
    # 1) Determine the service’s native CRS
    source_epsg = get_layer_crs(rest_url)

    # 2) Download GeoJSON
    resp = session.get(
        f"{rest_url}/query",
        params={"where":"1=1", "outFields":"*", "f":"geojson"}
    )
    resp.raise_for_status()
    features = resp.json().get("features", [])
    if not features:
        return []

    # 3) Build GeoDataFrame, honoring the true source EPSG
    gdf = gpd.GeoDataFrame.from_features(features).set_crs(epsg=source_epsg)

    # 4) Reproject to your target
    try:
        gdf.to_crs(epsg=target_epsg, inplace=True)
    except Exception as e:
        print(f"⚠️ Reproject failed ({source_epsg}→{target_epsg}): {e}")

    # 5) Return with a layer name
    layer_name = Path(rest_url).stem
    return [(layer_name, gdf)]

# 7) Helper: ArcGIS Item (GDB zip) → Shapefiles
def fetch_gdb_layers(url, target_epsg):
    """Download GDB zip and return list of (layer_name, GeoDataFrame)."""
    resp = session.get(url); resp.raise_for_status()

    zip_bytes = BytesIO(resp.content)
    temp_dir = output_dir / "temp_gdb"
    if temp_dir.exists(): shutil.rmtree(temp_dir)
    temp_dir.mkdir()
    with zipfile.ZipFile(zip_bytes) as z:
        z.extractall(temp_dir)

    gdb_path = next(temp_dir.glob("*.gdb"), None)
    results = []
    if not gdb_path:
        print(f"❌ No .gdb in {url}")
    else:
        for layer_name in fiona.listlayers(gdb_path):
            gdf = gpd.read_file(str(gdb_path), layer=layer_name)
            if gdf.empty:
                print(f"⚠️ {layer_name} empty, skipping")
                continue

            gdf.set_crs(epsg=4326, inplace=True)
            try:
                gdf.to_crs(epsg=target_epsg, inplace=True)
            except Exception as e:
                print(f"⚠️ {layer_name} reproj failed: {e}")

            results.append((layer_name, gdf))

    shutil.rmtree(temp_dir)
    return results

# 8) Main loop
total = len(layers)
gpkg = output_dir / "project_data.gpkg"
if engine is None and gpkg.exists(): gpkg.unlink()

for i, layer in enumerate(layers, start=1):
    name, url = layer["id"], layer["url"]
    stype     = layer.get("source_type", "arcgis_services")
    print(f"[{i}/{total}] Fetching {name} ({stype})")

    if stype == "arcgis_services":
        dfs = fetch_service_layer(url, output_epsg)
    elif stype == "arcgis_item":
        dfs = fetch_gdb_layers(url, output_epsg)
    else:
        continue

    for lname, gdf in dfs:
        if engine:
            print(f"→ Writing {lname} to PostGIS")
            gdf.to_postgis(lname, engine, if_exists="replace", index=False)
        else:
            print(f"→ Appending {lname} to GeoPackage")
            gdf.to_file(gpkg, layer=lname, driver="GPKG")

