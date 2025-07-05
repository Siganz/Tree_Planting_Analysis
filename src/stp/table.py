"""
Hello
"""
import csv
from datetime import datetime
from pathlib import Path

import fiona
import pandas as pd
from sqlalchemy import text

# ────────────────────────────────────────────────────────────────────────────────
# Metadata Recording Helpers
# ────────────────────────────────────────────────────────────────────────────────


def record_layer_metadata_db(engine, layer_id: str, url: str, source_epsg: int, service_wkid: int = None):
    """
    Inserts (layer_id, source_url, source_epsg, service_wkid, downloaded_at) 
    into a PostGIS table named 'layers_inventory'. 
    If the row with same layer_id already exists, does nothing.
    Assumes the table has columns (layer_id TEXT PRIMARY KEY, source_url TEXT,
    source_epsg INT, service_wkid INT, downloaded_at TIMESTAMP).
    """
    if engine is None:
        return

    stmt = text(
        """
        INSERT INTO layers_inventory (layer_id, source_url, source_epsg,
        service_wkid, downloaded_at)
        VALUES (:layer_id, :url, :epsg, :service_wkid, NOW())
        ON CONFLICT (layer_id) DO NOTHING;
        """
    )
    engine.execute(stmt, {
        "layer_id": layer_id,
        "url":      url,
        "epsg":     source_epsg,
        "service_wkid": service_wkid
    })


def record_layer_metadata_csv(csv_path: Path, layer_name: str, url: str,
                              source_epsg: int, service_wkid: int = None):
    """
    Appends a row to layers_inventory.csv with:
      layer_id, source_url, source_epsg, service_wkid, downloaded_at(UTC).
    Writes a header row if the CSV doesn’t already exist.
    """
    write_header = not csv_path.exists()
    with open(csv_path, "a", newline="") as f:
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
            layer_name,
            url,
            source_epsg,
            service_wkid if service_wkid is not None else "",
            datetime.utcnow().isoformat(),
        ])


def build_fields_inventory_gpkg(gpkg_path: Path) -> pd.DataFrame:
    """
    Returns a DataFrame with columns [layer_name, field_name, field_type]
    or every layer in the GPKG.
    """
    rows = []
    for layer in fiona.listlayers(str(gpkg_path)):
        with fiona.open(str(gpkg_path), layer=layer) as src:
            for fld, fld_type in src.schema["properties"].items():
                rows.append({
                    "layer_name": layer,
                    "field_name": fld,
                    "field_type": fld_type
                })
    return pd.DataFrame(rows)


def build_fields_inventory_postgis(engine, schema: str = "public") -> pd.DataFrame:
    """
    Returns a DataFrame with [layer_name, field_name, field_type] 
    for every table in PostGIS (public schema by default).
    """
    sql = text(f"""
        SELECT
            table_name   AS layer_name,
            column_name  AS field_name,
            data_type    AS field_type
        FROM information_schema.columns
        WHERE table_schema = :schema
        ORDER BY table_name, ordinal_position;
    """)
    df = pd.read_sql(sql, engine, params={"schema": schema})
    return df


def write_inventory(df: pd.DataFrame, out_csv: Path):
    """
    Takes a DataFrame (with columns layer_name, field_name, field_type) and writes it to CSV.
    """
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv, index=False)
    print(f"Schema inventory written to {out_csv}")