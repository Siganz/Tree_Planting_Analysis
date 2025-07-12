# _optional_deps.py
"""
optional
"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import geopandas as gpd
    import pandas as pd
else:
    try:
        import geopandas as gpd
        import pandas as pd
    except ImportError:  # pragma: no cover
        gpd = pd = None

GeoDataFrame = getattr(gpd, "GeoDataFrame", None)
DataFrame = getattr(pd, "DataFrame", None)
DATAFRAME_LIKE = "GeoDataFrame | DataFrame | None"
