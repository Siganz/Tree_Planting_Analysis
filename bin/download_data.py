"""
download_data.py

Main entry point for fetching spatial and tabular datasets based on a
configuration file and source registry. Supports Socrata, ArcGIS, and
direct URLs (CSV, GeoJSON, Shapefile, GPKG). Records metadata and
optionally reprojects in a GeoPackage or loads into PostGIS.
"""

import json
import logging
from pathlib import Path

# Read project configuration
from stp.config_loader import get_setting, get_constant

from helpers.download import (
    fetch_arcgis_table,
    fetch_arcgis_vector,
    fetch_csv_direct,
    fetch_gdb_or_zip,
    fetch_geojson_direct,
    fetch_gpkg_layers,
    dispatch_socrata_table as fetch_socrata_table
)

from helpers.storage import (
    get_geopackage_path,
    get_postgis_engine,
    reproject_all_layers,
    sanitize_layer_name,
)
from helpers.table import (
    record_layer_metadata_csv,
    record_layer_metadata_db,
)

logger = logging.getLogger(__name__)


# Dispatch map: (source_type, format) → fetch function
FETCHERS = {
    ("socrata", "csv"): fetch_socrata_table,
    ("socrata", "json"): fetch_socrata_table,
    ("socrata", "geojson"): fetch_socrata_vector,  # noqa: F821
    ("socrata", "shapefile"): fetch_socrata_vector,  # noqa: F821

    ("arcgis", "csv"): fetch_arcgis_table,
    ("arcgis", "json"): fetch_arcgis_table,
    ("arcgis", "geojson"): fetch_arcgis_vector,
    ("arcgis", "shapefile"): fetch_arcgis_vector,

    (None, "csv"): fetch_csv_direct,
    (None, "geojson"): fetch_geojson_direct,
    (None, "shapefile"): fetch_gdb_or_zip,
    (None, "gpkg"): fetch_gpkg_layers,
}


def setup_destinations():
    """Read config settings and prepare output destinations."""
    socrata_token = get_setting("socrata.app_token", required=True)
    db_cfg = get_setting("db", {})

    if db_cfg.get("enabled", False):
        db_engine = get_postgis_engine(db_cfg)
    else:
        db_engine = None

    output_epsg = get_setting("output_epsg", get_constant("nysp_epsg"))
    out_shp_dir = Path(get_setting("output_shapefile"))
    out_tbl_dir = Path(get_setting("output_tables"))
    out_shp_dir.mkdir(parents=True, exist_ok=True)
    out_tbl_dir.mkdir(parents=True, exist_ok=True)

    if not db_engine:
        metadata_csv = out_tbl_dir / get_constant(
            "data_inventory_filename"
        )
        gpkg = get_geopackage_path(out_shp_dir)
        if metadata_csv.exists():
            try:
                metadata_csv.unlink()
            except OSError as e:
                logger.warning(
                    "Could not delete existing CSV '%s': %s", metadata_csv, e
                )
    else:
        metadata_csv = None
        gpkg = None

    return socrata_token, db_engine, gpkg, metadata_csv, output_epsg


def load_layer_list():
    """Load the list of layers to fetch from the JSON registry."""
    data_sources = Path("config") / "data_sources.json"
    with open(data_sources, encoding="utf-8") as f:
        return json.load(f)


def process_layer(
    layer, idx, total, socrata_token, db_engine, gpkg, metadata_csv
):
    """Fetch, record metadata, and store one layer."""
    layer_id = layer["id"]
    url = layer["url"]
    stype = layer.get("source_type")
    fmt = layer.get("format", "").lower()
    helper_fn = FETCHERS.get((stype, fmt))

    logger.info(
        "[%d/%d] %s (source_type=%s, format=%s)",
        idx,
        total,
        layer_id,
        stype,
        fmt,
    )

    if stype == "arcgis":
        raw = fetch_arcgis_vector(url)
        results = [
            (layer_id, gdf, src_epsg, wkid)
            for (_, gdf, src_epsg, wkid) in raw
        ]
    elif stype == "socrata":
        raw = helper_fn(url, app_token=socrata_token)
        results = [
            (layer_id, gdf, src_epsg, None)
            for (_, gdf, src_epsg) in raw
        ]
    else:
        raw = helper_fn(url)
        results = [
            (layer_id, gdf, src_epsg, None)
            for (_, gdf, src_epsg) in raw
        ]

    for raw_name, gdf, source_epsg, service_wkid in results:
        clean_name = sanitize_layer_name(raw_name)

        if db_engine:
            record_layer_metadata_db(
                db_engine,
                clean_name,
                url,
                source_epsg,
                service_wkid,
            )
            gdf.to_postgis(
                clean_name,
                db_engine,
                if_exists="replace",
                index=False,
            )
        else:
            record_layer_metadata_csv(
                metadata_csv,
                clean_name,
                url,
                source_epsg,
                service_wkid,
            )
            export_spatial_layer(gdf, clean_name, gpkg)  # noqa: F821


def finalize(gpkg, metadata_csv, output_epsg):
    """Reproject all layers in the GeoPackage to the target EPSG."""
    if gpkg and metadata_csv:
        reproject_all_layers(gpkg, metadata_csv, target_epsg=output_epsg)


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    socrata_token, db_engine, gpkg, metadata_csv, output_epsg = (
        setup_destinations()
    )
    layers = load_layer_list()
    total = len(layers)
    for idx, layer in enumerate(layers, start=1):
        process_layer(
            layer,
            idx,
            total,
            socrata_token,
            db_engine,
            gpkg,
            metadata_csv,
        )
    finalize(gpkg, metadata_csv, output_epsg)


if __name__ == "__main__":
    main()
