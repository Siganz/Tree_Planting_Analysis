import types
import stp.http_client as hc


class DummyResponse:
    def __init__(self, data: bytes):
        self.content = data

    def raise_for_status(self):
        pass


def test_fetch_bytes(monkeypatch):
    def fake_get(url):
        return DummyResponse(b"ok")

    monkeypatch.setattr(hc._session, "get", fake_get)
    data = hc.fetch_bytes("http://example.com")
    assert data == b"ok"
