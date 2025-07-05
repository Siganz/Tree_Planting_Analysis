"""Simple HTTP client helpers."""

from typing import Optional

import requests

_session = requests.Session()


def fetch_bytes(
        url: str, *, session: Optional[requests.Session] = None) -> bytes:
    """Return response content for GET request."""
    sess = session or _session
    resp = sess.get(url)
    resp.raise_for_status()
    return resp.content
