"""CSV metadata recording functions."""

from __future__ import annotations

import csv
import logging
from datetime import datetime
from pathlib import Path

__all__ = ["record"]


def record(
        csv_path: Path,
        layer_id: str,
        url: str,
        source_epsg: int,
        service_wkid: int | None = None) -> None:
    """Append a row to ``layers_inventory.csv``.

    Parameters
    ----------
    csv_path:
        Destination CSV path.
    layer_id:
        Identifier for the layer being recorded.
    url:
        Source URL of the dataset.
    source_epsg:
        EPSG code of the dataset.
    service_wkid:
        Optional WKID from an ArcGIS service.
    """
    logger = logging.getLogger(__name__)
    write_header = not csv_path.exists()
    try:
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        with csv_path.open("a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if write_header:
                writer.writerow([
                    "layer_id",
                    "source_url",
                    "source_epsg",
                    "service_wkid",
                    "downloaded_at",
                ])
            writer.writerow([
                layer_id,
                url,
                source_epsg,
                service_wkid if service_wkid is not None else "",
                datetime.utcnow().isoformat(),
            ])
    except Exception as exc:  # pragma: no cover - log and continue
        logger.error("Failed to record metadata CSV %s: %s", csv_path, exc)
