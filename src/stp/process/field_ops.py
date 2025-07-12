"""Field operations for STP pipeline (attribute tweaks)."""

import logging

import geopandas as gpd

logging.basicConfig(level=logging.INFO)


def calculate_unique_blocks(
    gdf: gpd.GeoDataFrame,
    borough_field: str = 'Borough',
    block_field: str = 'Block',
    output_field: str = 'Unique_Blocks'
) -> gpd.GeoDataFrame:
    """Calculate unique blocks (concat Borough + Block, like CalculateField)."""
    gdf[output_field] = gdf[borough_field].astype(str) + gdf[block_field].astype(str)
    logging.info("Calculated %s", output_field)
    return gdf


def add_unique_parts(
    gdf: gpd.GeoDataFrame,
    unique_field: str = 'Unique_Blocks',
    output_field: str = 'Unique_Block_Parts'
) -> gpd.GeoDataFrame:
    """Add unique parts field(Unique_Blocks + index,
      like AddField + CalculateField)."""
    gdf[output_field] = gdf[unique_field].astype(str) + gdf.index.astype(str)
    logging.info("Added %s", output_field)
    return gdf


def delete_fields(
        gdf: gpd.GeoDataFrame, fields_to_drop: list
        ) -> gpd.GeoDataFrame:
    """Delete fields (like DeleteField). Drops specified columns."""
    gdf = gdf.drop(columns=fields_to_drop, errors='ignore')
    logging.info("Deleted fields")
    return gdf