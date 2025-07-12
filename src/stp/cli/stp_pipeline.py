import json
import logging
from pathlib import Path

import geopandas as gpd  # For handling spatial data

from core.config import get_setting  # To load config values
from fetch.arcgis import fetch_arcgis_vector  # ArcGIS fetcher
from fetch.csv import fetch_csv_direct  # CSV fetcher (if needed)
from fetch.geojson import fetch_geojson_direct  # GeoJSON fetcher
from stp.fetch.socrata import fetch_  # Socrata fetcher
from stp.fetch.socrata import dispatch_socrata_table
# Add more fetchers as needed from stp/fetch/



def load_sources() -> list[dict]:
    """Load the list of data sources from config/sources.json."""
    sources_path = Path("config/sources.json")
    if not sources_path.exists():
        raise FileNotFoundError(f"Config file not found: {sources_path}")
    with sources_path.open(encoding="utf-8") as file:
        return json.load(file)


def setup_logging_and_output() -> Path:
    """Set up logging and return the raw data output directory."""
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")
    output_dir = Path(get_setting("paths.output.raw", "data/raw"))
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


FETCHERS = {
    "socrata": fetch_socrata_json,
    "arcgis": fetch_arcgis_vector,
    "csv": fetch_csv_direct,
    "geojson": fetch_geojson_direct,
    # Add more as needed, e.g., "gdb": fetch_gdb, etc.
}


def download_source(source: dict, output_dir: Path) -> None:
    """Download and save a single source."""
    source_id = source["id"]
    url = source["url"]
    source_type = source.get("source_type", "").lower()
    fmt = source.get("format", "").lower()

    if source_type not in FETCHERS:
        logging.warning("Skipping unknown source type: %s (%s)",
                        source_type, source_id)
        return

    logging.info("Downloading %s from %s...", source_id, url)
    fetch_fn = FETCHERS[source_type]

    # Fetch the data (returns list of (name, gdf, epsg) tuples)
    results = fetch_fn(url)  # Add params like app_token if needed

    for raw_name, gdf, epsg in results:
        if gdf is None or gdf.empty:
            logging.warning("No data for %s", raw_name)
            continue

        # Save as GeoJSON (simple format; can change to GPKG later)
        save_path = output_dir / f"{source_id}.geojson"
        gdf.to_file(save_path, driver="GeoJSON")
        logging.info("Saved %s (EPSG: %s) to %s", source_id, epsg, save_path)


def main() -> None:
    """Main pipeline entry: Download all sources."""
    output_dir = setup_logging_and_output()
    sources = load_sources()

    for source in sources:
        download_source(source, output_dir)

    logging.info("Download complete! Files in %s", output_dir)


if __name__ == "__main__":
    main()