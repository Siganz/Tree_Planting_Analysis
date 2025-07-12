"""Address-related cleaning routines."""

from typing import Optional

import geopandas as gpd
import pandas as pd


def clean_street_signs(
    gdf: gpd.GeoDataFrame,
    *,
    require_record_type: str = "Current",
    date_fields: Optional[list[str]] = None,
    int_fields: Optional[list[str]] = None,
    drop_suffixes: Optional[list[str]] = None,
    keep_fields: Optional[list[str]] = None,
) -> gpd.GeoDataFrame:
    """Clean street sign records and drop non-current entries."""
    df = gdf.copy()
    if date_fields is None:
        date_fields = [
            "order_completed_on_date",
            "sign_design_voided_on_date",
        ]
    if int_fields is None:
        int_fields = ["distance_from_intersection"]
    if drop_suffixes is None:
        drop_suffixes = [
            "on_street_suffix",
            "from_street_suffix",
            "to_street_suffix",
        ]
    if keep_fields is None:
        keep_fields = [
            "order_number",
            "record_type",
            "order_type",
            "borough",
            "on_street",
            "from_street",
            "side_of_street",
            "order_completed_on_date",
            "sign_code",
            "sign_description",
            "sign_size",
            "sign_location",
            "distance_from_intersection",
            "arrow_direction",
            "sheeting_type",
            "support",
            "to_street",
            "facing_direction",
            "sign_notes",
            "sign_design_voided_on_date",
        ]
    df = df[df["record_type"].str.strip().str.title() == require_record_type]
    for fld in date_fields:
        if fld in df:
            df[fld] = pd.to_datetime(df[fld], errors="coerce")
    for fld in int_fields:
        if fld in df:
            df[fld] = pd.to_numeric(df[fld], errors="coerce")
    df = df.drop(columns=[c for c in drop_suffixes if c in df.columns])
    final_cols = [c for c in keep_fields if c in df.columns] + ["geometry"]
    df = df[final_cols].copy()
    df["record_type"] = df["record_type"].str.strip().str.title()
    df["side_of_street"] = df["side_of_street"].str.strip().str.upper()
    df["arrow_direction"] = df["arrow_direction"].str.strip()
    df["sign_description"] = df["sign_description"].str.strip()
    return gpd.GeoDataFrame(df, geometry="geometry", crs=gdf.crs)
