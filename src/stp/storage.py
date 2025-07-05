"""
storage.py — GeoDataFrame persistence & metadata helpers

This module contains utilities to write GeoDataFrames out to PostGIS,
GeoPackage files, and to reproject or inventory existing layers.

Functions:

  • get_postgis_engine(db_config: dict) → Optional[Engine]
      Create a SQLAlchemy Engine if the `db` config is enabled and complete,
      else return None.

  • get_geopackage_path(output_dir: Path, filename: str = "project_data.gpkg")
      Generate (and if existing, delete) a GeoPackage file path.

  • sanitize_layer_name(name: str) → str
      Clean a string to a valid layer name (alphanumeric + underscore,
      no leading digit, truncated to max length).

  • reproject_all_layers(
      gpkg_path: Path,
      metadata_csv: Path,
      target_epsg: int = DEFAULT_TARGET_EPSG
    )
      Read a layers‐inventory CSV, reproject each layer in the GPKG to
      `target_epsg`, and overwrite it in place.
"""

from pathlib import Path
from sqlalchemy import create_engine
import pandas as pd
import geopandas as gpd
from .settings import get_setting

LAYER_NAME_MAX_LENGTH = get_setting("layer_name_max_length")
DEFAULT_TARGET_EPSG = get_setting("nysp_epsg")

# ────────────────────────────────────────────────────────────────────────────────
# Database / Engine Helpers
# ────────────────────────────────────────────────────────────────────────────────


def get_postgis_engine(db_config: dict):
    """
    Returns a SQLAlchemy engine if db_config['enabled']
    is True and all required fields (driver, user, password,
    host, port, database) exist. Otherwise returns None.
    """
    if not db_config.get("enabled", False):
        return None

    driver = db_config.get("driver")
    user = db_config.get("user")
    password = db_config.get("password")
    host = db_config.get("host")
    port = db_config.get("port")
    database = db_config.get("database")

    if not all((driver, user, password, host, port, database)):
        return None

    url = f"{driver}://{user}:{password}@{host}:{port}/{database}"
    return create_engine(url)


def get_geopackage_path(
        output_dir: Path,
        filename: str = "project_data.gpkg"
        ) -> Path:
    """
    Returns a Path to a fresh GeoPackage file. If an existing file is present,
    attempts to delete it first. If deletion fails (e.g. file is locked),
    warns and continues.
    """
    gpkg = Path(output_dir) / filename
    if gpkg.exists():
        try:
            gpkg.unlink()
        except PermissionError as e:
            print(f"⚠️ Could not delete existing GeoPackage '{gpkg}': {e}")
    return gpkg

# ────────────────────────────────────────────────────────────────────────────────
# Utility / Geometry Helpers
# ────────────────────────────────────────────────────────────────────────────────


def sanitize_layer_name(name: str) -> str:
    """
    - Replace any non-alphanumeric or underscore with “_”
    - If it starts with a digit, prefix an underscore
    - Truncate to LAYER_NAME_MAX_LENGTH characters
    """
    safe = "".join(ch if (ch.isalnum() or ch == "_") else "_" for ch in name)
    if safe and safe[0].isdigit():
        safe = "_" + safe
    return safe[:LAYER_NAME_MAX_LENGTH]


# Need to include x/y coordinates for csv
def reproject_all_layers(gpkg_path: Path,
                         metadata_csv: Path,
                         target_epsg: int = DEFAULT_TARGET_EPSG):
    """
    Reads layers_inventory.csv to learn each layer’s original CRS (source_epsg)
    and, if available, service_wkid. Then:
      1) Open each layer from gpkg_path (raw GPKG, still in source_epsg)
      2) Assign or confirm the GeoDataFrame’s CRS = source_epsg
      3) Reproject to target_epsg
      4) Overwrite the layer in the GPKG with the new CRS embedded
    Prints a line for each layer, using service_wkid if provided.
    """
    meta = pd.read_csv(metadata_csv)
    for _, row in meta.iterrows():
        layer_name = row["layer_id"]
        source_epsg = int(row["source_epsg"])
        raw_wkid = row.get("service_wkid")
        # Convert service_wkid to int if not empty, else keep as ""
        try:
            service_wkid = int(raw_wkid) if raw_wkid not in (None, "") else ""
        except ValueError:
            service_wkid = ""

        # 1) Read the raw layer (GeoPackage) into a GeoDataFrame
        gdf = gpd.read_file(gpkg_path, layer=layer_name)
        if gdf.crs is None:
            gdf = gdf.set_crs(epsg=source_epsg, allow_override=True)
        else:
            gdf = gdf.to_crs(epsg=source_epsg)

        # 2) Reproject to target_epsg
        gdf = gdf.to_crs(epsg=target_epsg)

        # 3) Overwrite the layer in the GPKG
        gdf.to_file(gpkg_path, layer=layer_name, driver="GPKG")

        # 4) Print the reproject info
        if service_wkid:
            print(
                f"Reprojected '{layer_name}': "
                f"{service_wkid} → {target_epsg}")
        else:
            print(f"Reprojected '{layer_name}': "
                  f"{source_epsg} → {target_epsg}")
