"""Geometry operations for STP pipeline (shape-changing functions)."""

import logging

import geopandas as gpd

logging.basicConfig(level=logging.INFO)


def dissolve_gdf(gdf: gpd.GeoDataFrame, by_field: str, single_part: bool = True
                 ) -> gpd.GeoDataFrame:
    """Dissolve by field (like PairwiseDissolve).

    Groups features with same value in by_field, merging geometries.
    """
    dissolved = gdf.dissolve(by=by_field)
    if single_part:
        # Multipart to singlepart
        dissolved = dissolved.explode(ignore_index=True)
    logging.info("Dissolved by %s", by_field)
    return dissolved


def erase_gdf(input_gdf: gpd.GeoDataFrame, erase_gdf: gpd.GeoDataFrame
              ) -> gpd.GeoDataFrame:
    """Erase input by erase geometry (like PairwiseErase).

    Removes parts of input that overlap erase.
    """
    # unary_union combines erase shapes into one
    erased_geom = input_gdf.difference(erase_gdf.unary_union)
    erased = gpd.GeoDataFrame(
        geometry=erased_geom, crs=input_gdf.crs
        ).explode(ignore_index=True)
    logging.info("Erased geometries")
    return erased


def buffer_gdf(gdf: gpd.GeoDataFrame, distance: float
               ) -> gpd.GeoDataFrame:
    """Buffer geometries (like PairwiseBuffer).

    Adds a 'halo' around shapes.
    """
    buffered = gdf.buffer(distance)
    buffered_gdf = gpd.GeoDataFrame(geometry=buffered, crs=gdf.crs)
    logging.info("Buffered by %s", distance)
    return buffered_gdf


def intersect_gdf(input_gdf: gpd.GeoDataFrame, intersect_gdf: gpd.GeoDataFrame
                  ) -> gpd.GeoDataFrame:
    """Intersect (like PairwiseIntersect).

    Keeps overlapping parts, combines attributes.
    """
    intersected = gpd.overlay(input_gdf, intersect_gdf, how='intersection')
    logging.info("Intersected geometries")
    return intersected


def repair_geometry(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Repair invalid geometries (like RepairGeometry).

    Fixes issues like self-intersects or bad rings.
    """
    gdf['geometry'] = gdf.make_valid()
    logging.info("Repaired geometries")
    return gdf