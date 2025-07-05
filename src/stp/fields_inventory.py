"""
fields_inventory.py — Dump database or GeoPackage field schemas

This script reads the project’s configuration using
``stp.config_loader.get_setting`` to determine whether to extract a fields
inventory from a PostGIS database or a GeoPackage file.

Usage (run as a standalone script):
  1. Use :func:`stp.config_loader.get_setting` to read ``db`` settings and
     output paths.
  2. If PostGIS is enabled and connection parameters are valid:
       • Connect via SQLAlchemy and export the PostGIS schema to
         Data/tables/fields_inventory_postgis.csv
     Else:
       • Fall back to the GeoPackage at Data/shapefiles/project_data.gpkg
       • Export its layer field inventory to Data/tables/fields_inventory.csv

Dependencies:
  • SQLAlchemy
  • pandas
  • geopandas
"""

from pathlib import Path
from sqlalchemy import create_engine

from .inventory.gpkg import from_gpkg
from .inventory.postgis import from_postgis
from .inventory.export import to_csv
from .config_loader import get_setting, get_constant

if __name__ == "__main__":
    # 1) Resolve configuration settings using config_loader helpers
    db_cfg = get_setting("db", {})
    input_dir = Path(
        get_setting(
            "data.output_shapefile",
            get_constant("default_output_shapefile_dir"),
        )
    )
    input_dir.mkdir(parents=True, exist_ok=True)

    output_dir = Path(
        get_setting(
            "data.output_tables",
            get_constant("default_output_table_dir"),
        )
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    # 2) If PostGIS is enabled, dump PostGIS schema; otherwise dump GPKG schema
    if db_cfg.get("enabled", False):
        # Build a SQLAlchemy engine
        driver = db_cfg.get("driver")
        user = db_cfg.get("user")
        pwd = db_cfg.get("password")
        host = db_cfg.get("host")
        port = db_cfg.get("port")
        db = db_cfg.get("database")

        if all((driver, user, pwd, host, port, db)):
            engine = create_engine(
                f"{driver}://{user}:{pwd}@{host}:{port}/{db}"
            )
            df = from_postgis(engine, schema=db_cfg.get("schema", "public"))
            to_csv(df, output_dir / "fields_inventory_postgis.csv")
        else:
            print("PostGIS is enabled in config,"
                  "but missing connection parameters.")
    else:
        # Dump the GeoPackage schema
        gpkg = input_dir / get_constant("default_gpkg_name")
        if gpkg.exists():
            df = from_gpkg(gpkg)
            to_csv(df, output_dir / "fields_inventory.csv")
        else:
            print(f"No GeoPackage found at {gpkg}",
                  "→ cannot build fields inventory.")
