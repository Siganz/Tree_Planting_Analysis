"""Extract field inventory from a PostGIS database."""

from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.engine import Engine
import pandas as pd

__all__ = ["from_postgis"]


def from_postgis(engine: Engine, schema: str = "public") -> pd.DataFrame:
    """Return field inventory for all tables in a PostGIS schema."""
    sql = text(
        """
        SELECT table_name AS layer_name,
               column_name AS field_name,
               data_type AS field_type
        FROM information_schema.columns
        WHERE table_schema = :schema
        ORDER BY table_name, ordinal_position
        """
    )
    return pd.read_sql(sql, engine, params={"schema": schema})
