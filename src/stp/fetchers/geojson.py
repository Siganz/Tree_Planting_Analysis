"""GeoJSON direct download helper."""

from io import BytesIO
from pathlib import Path
from typing import List, Tuple
import logging

import geopandas as gpd
from fiona.errors import DriverError, FionaValueError

from .. import http_client
from ..file_storage import sanitize_layer_name
from ..settings import DEFAULT_EPSG

logger = logging.getLogger(__name__)


def fetch_geojson_direct(url: str) -> List[Tuple[str, gpd.GeoDataFrame, int]]:
    """Download and parse a GeoJSON URL."""
    data = http_client.fetch_bytes(url)
    try:
        gdf = gpd.read_file(BytesIO(data))
    except (FionaValueError, DriverError) as err:
        logger.warning("GeoJSON read failed for %s: %s", url, err)
        return []
    gdf.set_crs(epsg=DEFAULT_EPSG, inplace=True)
    layer_name = sanitize_layer_name(Path(url).stem)
    return [(layer_name, gdf, DEFAULT_EPSG)]
