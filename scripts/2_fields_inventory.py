from pathlib import Path
import yaml
from sqlalchemy import create_engine

from helpers.table_helpers import (
    build_fields_inventory_gpkg,
    build_fields_inventory_postgis,
    write_inventory,
)

if __name__ == "__main__":
    # 1) Read your config.yaml to see if PostGIS is enabled
    base_dir = Path.cwd()
    cfg_path = base_dir / "config" / "config.yaml"
    config = yaml.safe_load(open(cfg_path))

    db_cfg = config.get("db", {})
    input_dir = Path(config.get("output_shapefiles", "Data/shapefiles"))
    input_dir.mkdir(parents=True, exist_ok=True)

    output_dir = Path(config.get("output_tables", "Data/tables"))
    output_dir.mkdir(parents=True, exist_ok=True)

    # 2) If PostGIS is enabled, dump PostGIS schema; otherwise dump GPKG schema
    if db_cfg.get("enabled", False):
        # Build a SQLAlchemy engine
        driver   = db_cfg.get("driver")
        user     = db_cfg.get("user")
        pwd      = db_cfg.get("password")
        host     = db_cfg.get("host")
        port     = db_cfg.get("port")
        database = db_cfg.get("database")

        if all((driver, user, pwd, host, port, database)):
            engine = create_engine(f"{driver}://{user}:{pwd}@{host}:{port}/{database}")
            df = build_fields_inventory_postgis(engine, schema=db_cfg.get("schema", "public"))
            write_inventory(df, output_dir / "fields_inventory_postgis.csv")
        else:
            print("PostGIS is enabled in config, but missing connection parameters.")
    else:
        # Dump the GeoPackage schema (assuming download_data.py wrote project_data.gpkg here)
        gpkg = input_dir / "project_data.gpkg"
        if gpkg.exists():
            df = build_fields_inventory_gpkg(gpkg)
            write_inventory(df, output_dir / "fields_inventory.csv")
        else:
            print(f"No GeoPackage found at {gpkg} → cannot build fields inventory.")
