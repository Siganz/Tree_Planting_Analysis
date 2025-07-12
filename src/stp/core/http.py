"""
HTTP client utilities with retries.
"""

from enum import IntEnum
import logging
from typing import Any, Dict, Optional, Tuple

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

_session: requests.Session = requests.Session()  # Global session


def fetch_bytes(
    url: str,
    *,
    session: Optional[requests.Session] = None,
) -> bytes:
    """Return response content for a GET request."""
    sess = session or _session
    resp = sess.get(url, timeout=30)
    resp.raise_for_status()
    return resp.content


def fetch_json_with_retry(
    url: str,
    *,
    params: Optional[Dict[str, Any]] = None,
    max_retries: int = 3,
    backoff_factor: float = 0.3,
    status_forcelist: Tuple[int, ...] = (429, 500, 502, 503, 504),
) -> Dict[str, Any]:
    """
    Fetch JSON from a URL with retries on transient errors.

    Parameters
    ----------
    url : str
        The URL to fetch.
    params : Dict[str, Any], optional
        Query parameters.
    max_retries : int, optional
        Maximum retry attempts (default 3).
    backoff_factor : float, optional
        Backoff multiplier (default 0.3).
    status_forcelist : Tuple[int, ...], optional
        HTTP status codes to retry on.

    Returns
    -------
    Dict[str, Any]
        Parsed JSON response.

    Raises
    ------
    requests.RequestException
        If all retries fail.
    """
    retry_strategy = Retry(
        total=max_retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=["GET"],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    sess = requests.Session()
    sess.mount("https://", adapter)
    sess.mount("http://", adapter)

    resp = sess.get(url, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()
