"""File-based GeoDataFrame helpers."""

from pathlib import Path

import geopandas as gpd
import pandas as pd

__all__ = [
    "get_geopackage_path",
    "sanitize_layer_name",
    "export_spatial_layer",
    "reproject_all_layers",
]

LAYER_NAME_MAX_LENGTH = 60


def get_geopackage_path(
    output_dir: Path, filename: str = "project_data.gpkg"
) -> Path:
    """Return a fresh GeoPackage path under *output_dir*."""
    gpkg = Path(output_dir) / filename
    if gpkg.exists():
        try:
            gpkg.unlink()
        except PermissionError as err:
            print(f"\u26a0\ufe0f Could not delete '{gpkg}': {err}")
    return gpkg


def sanitize_layer_name(name: str) -> str:
    """Return *name* cleaned for file or database layers."""
    safe = "".join(ch if (ch.isalnum() or ch == "_") else "_" for ch in name)
    if safe and safe[0].isdigit():
        safe = "_" + safe
    return safe[:LAYER_NAME_MAX_LENGTH]


def export_spatial_layer(gdf: gpd.GeoDataFrame, layer_name: str,
                         gpkg_path: Path) -> None:
    """Write ``gdf`` to ``gpkg_path`` under ``layer_name``."""
    gdf.to_file(gpkg_path, layer=layer_name, driver="GPKG")


def reproject_all_layers(
    gpkg_path: Path, metadata_csv: Path, target_epsg: int
) -> None:
    """Reproject each layer in the GeoPackage in place."""
    meta = pd.read_csv(metadata_csv)
    for _, row in meta.iterrows():
        layer_name = row["layer_id"]
        source_epsg = int(row["source_epsg"])
        raw_wkid = row.get("service_wkid")
        try:
            service_wkid = int(raw_wkid) if raw_wkid not in (None, "") else ""
        except ValueError:
            service_wkid = ""
        gdf = gpd.read_file(gpkg_path, layer=layer_name)
        if gdf.crs is None:
            gdf = gdf.set_crs(epsg=source_epsg, allow_override=True)
        else:
            gdf = gdf.to_crs(epsg=source_epsg)
        gdf = gdf.to_crs(epsg=target_epsg)
        gdf.to_file(gpkg_path, layer=layer_name, driver="GPKG")
        if service_wkid:
            print(
                f"Reprojected '{layer_name}': {service_wkid} → {target_epsg}"
            )
        else:
            print(
                f"Reprojected '{layer_name}': {source_epsg} → {target_epsg}"
            )
