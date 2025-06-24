import geopandas as gpd
from pathlib import Path

from data_cleaning_helpers import clean_street_signs

BASE_DIR = Path(__file__).resolve().parent.parent
GPKG = BASE_DIR / "data" / "shapefiles" / "project_data.gpkg"

# 1. Read the street_sign layer
gdf = gpd.read_file(GPKG, layer="street_sign")

ss_clean = clean_street_signs(gdf)

ss_clean.to_file(GPKG, layer="street_signs_current", driver="GPKG")