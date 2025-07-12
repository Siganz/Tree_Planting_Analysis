"""CSV direct download helper."""

from io import BytesIO
from pathlib import Path
from typing import List, Tuple
import logging

import geopandas as gpd
import pandas as pd
from pandas.errors import ParserError
from shapely.geometry import Point

from ..core import http
from ..storage.file_storage import sanitize_layer_name
from ..core import DEFAULT_EPSG #TODO use config.py to get default values

logger = logging.getLogger(__name__)


def fetch_csv_direct(url: str) -> List[Tuple[str, gpd.GeoDataFrame, int]]:
    """Download and parse a CSV URL."""
    data = http.fetch_bytes(url)
    try:
        df = pd.read_csv(BytesIO(data))
    except ParserError as err:
        logger.warning("CSV parse failed for %s: %s", url, err)
        return []
    if "latitude" not in df.columns or "longitude" not in df.columns:
        return []
    geometry = [Point(xy) for xy in zip(df.longitude, df.latitude)]
    gdf = gpd.GeoDataFrame(
        df.drop(columns=["latitude", "longitude"]),
        geometry=geometry,
        crs=f"EPSG:{DEFAULT_EPSG}",
    )
    layer_name = sanitize_layer_name(Path(url).stem)
    return [(layer_name, gdf, DEFAULT_EPSG)]
