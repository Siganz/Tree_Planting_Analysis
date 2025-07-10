import geopandas as gpd
from shapely.geometry import Point
import stp.fetch.geojson as gj


def test_fetch_geojson_direct(monkeypatch):
    def fake_bytes(url):
        return b"{}"

    monkeypatch.setattr(gj.http_client, "fetch_bytes", fake_bytes)
    dummy = gpd.GeoDataFrame({"geometry": [Point(0, 0)]}, geometry="geometry")

    def fake_read_file(buf):
        return dummy

    monkeypatch.setattr(gpd, "read_file", lambda *a, **k: dummy)
    res = gj.fetch_geojson_direct("http://x/data.geojson")
    assert res[0][0] == "data"
    assert res[0][1] is dummy
    assert res[0][2] == gj.DEFAULT_EPSG
