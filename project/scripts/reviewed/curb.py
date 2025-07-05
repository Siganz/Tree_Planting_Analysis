"""Generate curb polygons around lines using GeoPandas/Shapely."""
import math
from pathlib import Path

import geopandas as gpd
import yaml
from shapely.geometry import Polygon

def get_dominant_segment_angle(line):
    """Return angle (radians) of the longest segment in a LineString."""
    max_len = 0.0
    best_angle = 0.0
    coords = list(line.coords)
    for (x1, y1), (x2, y2) in zip(coords[:-1], coords[1:]):
        dx = x2 - x1
        dy = y2 - y1
        seg_len = math.hypot(dx, dy)
        if seg_len > max_len:
            max_len = seg_len
            best_angle = math.atan2(dy, dx)
    return best_angle

def generate_polygons(lines_gdf, extension_distance, buffer_width):
    """Return GeoDataFrame of rectangles around each line."""
    polys = []
    for line in lines_gdf.geometry:
        if line is None or len(line.coords) < 2:
            continue

        angle = get_dominant_segment_angle(line)
        sx, sy = line.coords[0]
        ex, ey = line.coords[-1]

        # Extend line ends
        sx -= extension_distance * math.cos(angle)
        sy -= extension_distance * math.sin(angle)
        ex += extension_distance * math.cos(angle)
        ey += extension_distance * math.sin(angle)

        # Buffer offset
        dx = (buffer_width / 2.0) * math.sin(angle)
        dy = (buffer_width / 2.0) * math.cos(angle)

        points = [
            (sx - dx, sy + dy),
            (ex - dx, ey + dy),
            (ex + dx, ey - dy),
            (sx + dx, sy - dy),
        ]
        polys.append(Polygon(points))

    return gpd.GeoDataFrame({"geometry": polys}, crs=lines_gdf.crs)

def main():
    """Entry point for CLI usage: build curb buffer polygons."""
    base_dir = Path.cwd()
    cfg_path = base_dir / "config" / "config.yaml"
    with open(cfg_path) as f:
        config = yaml.safe_load(f)

    curb_cfg = config.get("curb", {})
    ext_dist = float(curb_cfg.get("extension_distance", 0))
    buff_width = float(curb_cfg.get("buffer_width", 0))

    out_dir = Path(config.get("output_shapefiles", "Data/shapefiles"))
    gpkg = out_dir / "project_data.gpkg"

    lines = gpd.read_file(gpkg, layer="curb")
    polys = generate_polygons(lines, ext_dist, buff_width)

    polys.to_file(gpkg, layer="curb_buffer", driver="GPKG")
    print(f"✅ wrote {gpkg} layer 'curb_buffer'")

    return gpkg


if __name__ == "__main__":
    main()
