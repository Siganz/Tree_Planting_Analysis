import geopandas as gpd
from shapely.geometry import Point
import stp.cleaning.address as addr


def test_clean_street_signs():
    df = gpd.GeoDataFrame(
        {
            "record_type": ["Current"],
            "order_completed_on_date": ["2020-01-01"],
            "sign_description": ["desc"],
            "distance_from_intersection": ["1"],
            "side_of_street": ["N"],
            "arrow_direction": ["E"],
            "sign_code": ["A"],
            "sign_notes": ["note"],
        },
        geometry=[Point(0, 0)],
    )
    cleaned = addr.clean_street_signs(df)
    assert not cleaned.empty
