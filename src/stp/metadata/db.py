"""Database metadata recording functions."""

from __future__ import annotations

import logging
from sqlalchemy.engine import Engine
from sqlalchemy import text

__all__ = ["record"]


def record(
        engine: Engine,
        layer_id: str,
        url: str,
        source_epsg: int,
        service_wkid: int | None = None) -> None:
    """Insert a row into the ``layers_inventory`` table.

    Parameters
    ----------
    engine:
        SQLAlchemy database engine.
    layer_id:
        Identifier for the layer being recorded.
    url:
        Source URL of the dataset.
    source_epsg:
        EPSG code of the dataset.
    service_wkid:
        Optional WKID from an ArcGIS service.
    """
    if engine is None:
        return

    logger = logging.getLogger(__name__)
    stmt = text(
        """
        INSERT INTO layers_inventory (
            layer_id, source_url, source_epsg, service_wkid, downloaded_at
        ) VALUES (
            :layer_id, :url, :epsg, :service_wkid, NOW()
        )
        ON CONFLICT (layer_id) DO NOTHING
        """
    )
    try:
        engine.execute(
            stmt,
            {
                "layer_id": layer_id,
                "url": url,
                "epsg": source_epsg,
                "service_wkid": service_wkid,
            },
        )
    except Exception as exc:  # pragma: no cover - log and continue
        logger.error("Failed to record metadata for %s: %s", layer_id, exc)
