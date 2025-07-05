import geopandas as gpd
from shapely.geometry import Point
import stp.cleaning.trees as trees


def test_clean_trees_basic():
    df = gpd.GeoDataFrame(
        {"tpstructure": ["Full"], "objectid": [1]},
        geometry=[Point(0, 0)],
    )
    res = trees.clean_trees_basic(df)
    assert "TreeID" in res


def test_canceled_work_orders():
    df = gpd.GeoDataFrame(
        {
            "wotype": ["Tree Plant-Street Tree"],
            "wocategory": ["Tree Planting"],
            "wostatus": ["Cancel"],
            "objectid": [1],
        },
        geometry=[Point(0, 0)],
    )
    out = trees.canceled_work_orders(df)
    assert not out.empty
