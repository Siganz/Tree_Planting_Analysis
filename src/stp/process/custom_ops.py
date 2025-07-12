"""Custom operations for STP pipeline (special/complex functions)."""

import logging

import geopandas as gpd
from pygeoops import centerline
# pip install pygeoops (medial axis for polygon centerlines)

logging.basicConfig(level=logging.INFO)


def collapse_to_centerline(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Collapse polygons to centerlines (like CollapseHydroPolygon).

    Extracts medial axis (midpoints between edges).
    """
    centerlines = []
    for geom in gdf.geometry:
        if geom.is_valid and not geom.is_empty:
            cl = centerline(geom)
            if cl:
                centerlines.append(cl)
    collapsed = gpd.GeoDataFrame(geometry=centerlines, crs=gdf.crs)
    logging.info("Collapsed to centerlines")
    return collapsed