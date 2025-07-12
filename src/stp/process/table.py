"""Backward-compatible passthroughs for inventory and metadata helpers."""

from __future__ import annotations

from ..record.db import record as record_layer_metadata_db
from ..record.csv import record as record_layer_metadata_csv
from ..fetch.gpkg import (
    from_gpkg as build_fields_inventory_gpkg,
)
from ..fetch.postgis import (
    from_postgis as build_fields_inventory_postgis,
)
from ..fetch.export import to_csv as write_inventory

__all__ = [
    "record_layer_metadata_db",
    "record_layer_metadata_csv",
    "build_fields_inventory_gpkg",
    "build_fields_inventory_postgis",
    "write_inventory",
]
