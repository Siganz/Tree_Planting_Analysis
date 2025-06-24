import sys
from pathlib import Path

import yaml
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# ——— load config ———
# assume this script lives in scripts/, so repo root is one up
repo_root = Path(__file__).parent.parent
cfg_path = repo_root / "config" / "config.yaml"

with open(cfg_path, "r") as f:
    cfg = yaml.safe_load(f)

ss_cfg = cfg["street_signs"]
inp = ss_cfg["input"]
out = ss_cfg["output"]

# ——— read input layer ———
gdf = gpd.read_file(inp["path"], layer=inp["layer"])

# ——— validate required fields ———
for fld in ("NEAR_X", "NEAR_Y"):
    if fld not in gdf.columns:
        sys.exit(f"ERROR: required field {fld} not found in {inp['layer']}")

# ——— move points ———
def move_point(row):
    x, y = row["NEAR_X"], row["NEAR_Y"]
    if pd.notna(x) and pd.notna(y):
        return Point(x, y)
    return row.geometry  # leave unchanged if no near coords

gdf["geometry"] = gdf.apply(move_point, axis=1)

# ——— write output layer ———
gdf.to_file(
    out["path"],
    layer=out["layer"],
    driver="GPKG",
    index=False
)

print(f"✅ Wrote moved points to {out['path']} ({out['layer']})")
