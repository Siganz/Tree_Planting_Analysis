import yaml
import json
from pathlib import Path
import geopandas as gpd
from sqlalchemy import create_engine
from shapely.ops import unary_union

# 1) Paths and config
base_dir = Path.cwd()
config = yaml.safe_load(open(base_dir / "config" / "config.yaml"))
db_cfg = config.get("db", {})
output_epsg = config.get("output_epsg", 2263)
output_dir = Path(config.get("output_dir", "Data/shapefiles"))
output_dir.mkdir(parents=True, exist_ok=True)

# 2) Setup storage mode
engine = None
if db_cfg.get("enabled"):
    conn_url = (
        f"{db_cfg['driver']}://{db_cfg['user']}:{db_cfg['password']}@"
        f"{db_cfg['host']}:{db_cfg['port']}/{db_cfg['database']}"
    )
    engine = create_engine(conn_url)
else:
    gpkg_path = output_dir / "project_data.gpkg"
    if gpkg_path.exists():
        gpkg_path.unlink()

# 3) Define layers to process
layer_ids = [
    "borough", "community_districts", "city_council_districts",
    "us_congressional_districts", "state_senate_districts",
    "state_assembly_districts", "community_district_tabulation_areas",
    "neighborhood_tabulation_areas", "census_tracts", "census_blocks",
    "zoning_districts", "commercial_districts", "special_purpose_districts"
]

# 4) Load each layer into GeoDataFrames
gdfs = []
for layer in layer_ids:
    if engine:
        # Read from PostGIS
        gdf = gpd.read_postgis(f"SELECT * FROM {layer}", engine, geom_col='geometry')
        gdf.set_crs(epsg=output_epsg, inplace=True)
    else:
        # Read from GeoPackage
        gdf = gpd.read_file(gpkg_path, layer=layer)
    gdfs.append(gdf)

# 5) Union all boundaries
all_union = unary_union([gdf.unary_union for gdf in gdfs])
result_gdf = gpd.GeoDataFrame([{"geometry": all_union}], crs=output_epsg)

# 6) Persist the result
if engine:
    result_gdf.to_postgis("political_boundaries", engine, if_exists="replace", index=False)
else:
    result_gdf.to_file(gpkg_path, layer="political_boundaries", driver="GPKG")

print("✅ political_boundaries created")
