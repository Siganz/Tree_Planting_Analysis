from datetime import datetime
from pathlib import Path
import json
import yaml
import time
import os

from helpers.download import (
    fetch_socrata_table,
    fetch_socrata_vector,
    fetch_arcgis_table,
    fetch_arcgis_vector,
    fetch_geojson_direct,
    fetch_csv_direct,
    fetch_gpkg_layers,
    fetch_gdb_or_zip,
    export_spatial_layer,
)
from helpers.storage import (
    get_postgis_engine,
    get_geopackage_path,
    sanitize_layer_name,
    reproject_all_layers,
)
from helpers.table import (
    record_layer_metadata_csv,
    record_layer_metadata_db
)

def main():
    # ────────────────────────────────────────────────────────────────────────────────
    # 0) Startup / Timing
    # ────────────────────────────────────────────────────────────────────────────────

    start = time.time()
    starttime = datetime.now()
    print("Start Time:", starttime.strftime("%H:%M:%S"))

    # ────────────────────────────────────────────────────────────────────────────────
    # 1) Load config
    # ────────────────────────────────────────────────────────────────────────────────
    base_dir = Path.cwd()
    config_path = base_dir / "config" / "config.yaml"
    data_sources_path = base_dir / "config" / "data_sources.json"

    with open(config_path) as f:
        config = yaml.safe_load(f)

    socrata_token = config.get("socrata", {}).get("app_token")
    db_cfg = config.get("db", {})

    # ────────────────────────────────────────────────────────────────────────────────
    # 2) Decide PostGIS vs GeoPackage
    # ────────────────────────────────────────────────────────────────────────────────

    if db_cfg.get("enabled", False):
        db_engine = get_postgis_engine(db_cfg)
    else:
        db_engine = None

    output_epsg = config.get("output_epsg", 2263)
    output_shapefiles = Path(config.get("output_shapefiles", "Data/shapefiles"))
    output_shapefiles.mkdir(parents=True, exist_ok=True)
    output_tables = Path(config.get("output_tables", "Data/tables"))
    output_tables.mkdir(parents=True, exist_ok=True)

    if not db_engine:
        # We’ll write a GeoPackage + CSV metadata
        metadata_csv = output_tables / "data_inventory.csv"
        gpkg = get_geopackage_path(output_shapefiles)
    else:
        # We’ll record into PostGIS and skip GeoPackage/CSV
        metadata_csv = None
        gpkg = None

    # Wipe out any existing CSV before starting
    if metadata_csv and metadata_csv.exists():
        try:
            metadata_csv.unlink()
        except Exception as e:
            print(f"⚠️ Could not delete existing CSV '{metadata_csv}': {e}")

    # ────────────────────────────────────────────────────────────────────────────────
    # 3) Load “layers” from JSON
    # ────────────────────────────────────────────────────────────────────────────────

    with open(data_sources_path) as f:
        layers = json.load(f)

    # ────────────────────────────────────────────────────────────────────────────────
    # 4) Dispatch map: (source_type, format) → helper function
    # ────────────────────────────────────────────────────────────────────────────────

    HELPER_MAP = {
        ("socrata",  "csv"):       fetch_socrata_table,
        ("socrata",  "json"):      fetch_socrata_table,
        ("socrata",  "geojson"):   fetch_socrata_vector,
        ("socrata",  "shapefile"): fetch_socrata_vector,

        ("arcgis",   "csv"):       fetch_arcgis_table,
        ("arcgis",   "json"):      fetch_arcgis_table,
        ("arcgis",   "geojson"):   fetch_arcgis_vector,
        ("arcgis",   "shapefile"): fetch_arcgis_vector,

        (None,       "csv"):       fetch_csv_direct,
        (None,       "geojson"):   fetch_geojson_direct,
        (None,       "shapefile"): fetch_gdb_or_zip,
        (None,       "gpkg"):      fetch_gpkg_layers,
    }

    # ────────────────────────────────────────────────────────────────────────────────
    # 5) Main download loop
    # ────────────────────────────────────────────────────────────────────────────────

    for idx, layer in enumerate(layers, start=1):
        layer_id = layer["id"]
        url = layer["url"]
        stype = layer.get("source_type")        # e.g. "socrata" or "arcgis"
        fmt = layer.get("format", "").lower()   # e.g. "csv", "geojson", "shapefile"
        helper_fn = HELPER_MAP.get((stype, fmt))

        print(f"[{idx}/{len(layers)}] {layer_id} → (stype={stype}, format={fmt})")
        if not helper_fn:
            print(f"⚠️ No helper for {(stype, fmt)}; skipping.")
            continue

        # ─────────────────────────────────────────────────────────────────────────────
        # 5a) Call the fetcher. It returns different‐shaped tuples depending on stype.
        # ─────────────────────────────────────────────────────────────────────────────

        if stype == "arcgis":
            raw_results = fetch_arcgis_vector(url)
            # raw_results looks like [(None, gdf_full, 4326, native_wkid)]
            results = [
                (layer_id, gdf, source_epsg, service_wkid)
                for (_, gdf, source_epsg, service_wkid) in raw_results
            ]

        elif stype == "socrata":
            # fetch_socrata_table or _vector all return [(some_name, gdf, source_epsg)]
            raw_results = helper_fn(url, app_token=socrata_token)
            # Tag each with this layer_id and no service_wkid
            results = [
                (layer_id, gdf, source_epsg, None)
                for (_, gdf, source_epsg) in raw_results
            ]

        else:
            # f.eks. direct GeoJSON/CSV/GPKG/... → returns [(some_name, gdf, source_epsg)]
            raw_results = helper_fn(url)
            results = [
                (layer_id, gdf, source_epsg, None)
                for (_, gdf, source_epsg) in raw_results
            ]

        # ─────────────────────────────────────────────────────────────────────────────
        # 5b) For each tuple: sanitize, record metadata, and write
        # ─────────────────────────────────────────────────────────────────────────────

        for raw_name, gdf, source_epsg, service_wkid in results:
            clean_name = sanitize_layer_name(raw_name)

            # 1) Record metadata
            if db_engine:
                record_layer_metadata_db(
                    db_engine,
                    clean_name,
                    url,
                    source_epsg,
                    service_wkid
                )
            else:
                record_layer_metadata_csv(
                    metadata_csv,
                    clean_name,
                    url,
                    source_epsg,
                    service_wkid
                )

            # 2) Persist the GeoDataFrame (unreprojected) to PostGIS or GPKG
            if db_engine:
                # In PostGIS mode, this will write a table named clean_name
                gdf.to_postgis(clean_name, db_engine, if_exists="replace", index=False)
            else:
                # In GeoPackage mode, write to the .gpkg under layer=clean_name
                export_spatial_layer(gdf, clean_name, gpkg) 

    # ────────────────────────────────────────────────────────────────────────────────
    # 6) After loop: reproject all layers in the GPKG to output_epsg
    # ────────────────────────────────────────────────────────────────────────────────

    if gpkg and metadata_csv:
        reproject_all_layers(gpkg, metadata_csv, target_epsg=output_epsg)

    # ────────────────────────────────────────────────────────────────────────────────
    # 7) Timing / shutdown
    # ────────────────────────────────────────────────────────────────────────────────

    endtime = datetime.now()
    print("End Time:", endtime.strftime("%H:%M:%S"))

    elapsed = time.time() - start
    print(f"Elapsed time: {elapsed:.2f} seconds")

if __name__ == "__main__":
    main()