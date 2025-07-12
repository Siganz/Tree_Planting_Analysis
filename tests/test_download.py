import stp.fetch.download as dl


def test_fetch_direct_dispatch(monkeypatch):
    monkeypatch.setattr(
        dl,
        "fetch_geojson_direct",
        lambda url: [("a", None, 1)],
    )
    monkeypatch.setattr(dl, "fetch_csv_direct", lambda url: [("b", None, 1)])

    assert dl.fetch_direct("file.geojson")[0][0] == "a"
    assert dl.fetch_direct("file.csv")[0][0] == "b"
