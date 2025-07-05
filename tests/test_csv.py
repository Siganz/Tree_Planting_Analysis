"""
tests csv
"""
import geopandas as gpd
from pytest import MonkeyPatch
import stp.fetchers.csv as csv_f


def test_fetch_csv_direct(monkeypatch: MonkeyPatch):
    """Verify fetch_csv_direct returns [] when CSV lacks lat/lon cols."""
    csv_data = b"latitude,longitude\n1,2\n"

    def fake_bytes(url):
        return csv_data

    monkeypatch.setattr(csv_f.http_client, "fetch_bytes", fake_bytes)
    res = csv_f.fetch_csv_direct("http://x/data.csv")
    assert res[0][0] == "data"
    assert isinstance(res[0][1], gpd.GeoDataFrame)
    assert res[0][2] == csv_f.DEFAULT_EPSG
