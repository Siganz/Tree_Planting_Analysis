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

# use get_setting (aliased to 'get') so both settings.yaml overrides and
# defaults.yaml fallbacks work the same way
from stp.config_loader import get_setting as get, get_constant

from stp.fetchers import fetch_arcgis_vector

from stp.storage.file_storage import (
    get_geopackage_path,
    get_postgis_engine,
    reproject_all_layers,
    sanitize_layer_name,
    export_spatial_layer,
)
from stp.table import (
    record_layer_metadata_csv,
    record_layer_metadata_db,
)
from stp.scripts.download_utils import FETCHERS

logger = logging.getLogger(__name__)


def setup_destinations():
    """Read config settings and prepare output destinations."""
    socrata_token = get("socrata.app_token")
    db_cfg = get("db", {})

    if db_cfg.get("enabled", False):
        db_engine = get_postgis_engine(db_cfg)
    else:
        db_engine = None

    output_epsg = get("data.output_epsg", get_constant("nysp_epsg"))
    out_shp_dir = Path(get("data.output_shapefile"))
    out_tbl_dir = Path(get("data.output_tables"))
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
    data_sources = Path("config") / "sources.json"
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
            export_spatial_layer(gdf, clean_name, gpkg)


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
