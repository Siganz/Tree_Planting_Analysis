import stp.storrage.db_storage as dbs


def test_get_postgis_engine(monkeypatch):
    captured = {}

    def fake_create(url):
        captured["url"] = url
        return "engine"

    monkeypatch.setattr(dbs, "create_engine", fake_create)
    cfg = {
        "enabled": True,
        "driver": "postgis",
        "user": "u",
        "password": "p",
        "host": "h",
        "port": "1",
        "database": "d",
    }
    engine = dbs.get_postgis_engine(cfg)
    assert engine == "engine"
    assert "postgis://u:p@h:1/d" == captured["url"]

    cfg["enabled"] = False
    assert dbs.get_postgis_engine(cfg) is None
