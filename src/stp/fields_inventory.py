"""
fields_inventory.py — Dump database or GeoPackage field schemas

This script reads the project’s configuration to determine whether to
extract a fields inventory from a PostGIS database or a GeoPackage file.

Usage (run as a standalone script):
  1. Load `config/config.yaml` to read the `db` settings and output paths.
  2. If PostGIS is enabled and connection parameters are valid:
       • Connect via SQLAlchemy and export the PostGIS schema to
         Data/tables/fields_inventory_postgis.csv
     Else:
       • Fall back to the GeoPackage at Data/shapefiles/project_data.gpkg
       • Export its layer field inventory to Data/tables/fields_inventory.csv

Dependencies:
  • PyYAML
  • SQLAlchemy
  • pandas
  • geopandas
"""

from pathlib import Path
import yaml
from sqlalchemy import create_engine

from .table import (
    build_fields_inventory_gpkg,
    build_fields_inventory_postgis,
    write_inventory,
)

if __name__ == "__main__":
    # 1) Read your config.yaml to see if PostGIS is enabled
    base_dir = Path.cwd()
    cfg_path = base_dir / "config" / "config.yaml"
    with open(cfg_path, encoding='utf-8') as cfg_file:
        config = yaml.safe_load(cfg_file) or {}
    db_cfg = config.get("db", {})
    input_dir = Path(config.get("output_shapefiles", "Data/shapefiles"))
    input_dir.mkdir(parents=True, exist_ok=True)

    output_dir = Path(config.get("output_tables", "Data/tables"))
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
            df = build_fields_inventory_postgis(
                engine, schema=db_cfg.get("schema", "public")
            )
            write_inventory(df, output_dir / "fields_inventory_postgis.csv")
        else:
            print("PostGIS is enabled in config,"
                  "but missing connection parameters.")
    else:
        # Dump the GeoPackage schema
        gpkg = input_dir / "project_data.gpkg"
        if gpkg.exists():
            df = build_fields_inventory_gpkg(gpkg)
            write_inventory(df, output_dir / "fields_inventory.csv")
        else:
            print(f"No GeoPackage found at {gpkg}",
                  "→ cannot build fields inventory.")
