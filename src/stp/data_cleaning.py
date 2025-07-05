# data_cleaning.py

from typing import Optional

import geopandas as gpd
import pandas as pd
from .settings import get_setting

MIN_DBH = get_setting("min_dbh")


def clean_trees_basic(
    trees: gpd.GeoDataFrame,
    *,
    structure_field: str = "tpstructure",
    require_structure: str = "Full",
    id_field: str = "objectid",
    out_id: str = "TreeID"
) -> gpd.GeoDataFrame:
    """Return trees with full structure as a GeoDataFrame."""
    df = trees.loc[trees[structure_field] == require_structure,
                   [id_field, "geometry"]].copy()
    return df.rename(columns={id_field: out_id})


def clean_trees_advanced(
    trees: gpd.GeoDataFrame,
    planting_spaces: gpd.GeoDataFrame,
    *,
    # tree filters
    condition_field: str = "tpcondition",
    drop_conditions: Optional[list[str]] = None,
    structure_field: str = "tpstructure",
    require_structure: str = "Full",
    dbh_field: str = "dbh",
    min_dbh: float = MIN_DBH,
    # planting-space join
    ps_key: str = "plantingspaceglobalid",
    ps_globalid: str = "globalid",
    ps_status_field: str = "psstatus",
    keep_ps_status: str = "Populated",
    ps_jur_field: str = "jurisdiction",
    exclude_jur: str = "Private",
    # output
    id_field: str = "objectid",
    out_id: str = "TreeID"
) -> gpd.GeoDataFrame:
    """Return cleaned trees joined to planting spaces and filtered by DBH."""

    if drop_conditions is None:
        drop_conditions = ["Unknown", "Dead"]

    # 1–3: tree filters
    mask = (
        ~trees[condition_field].isin(drop_conditions) &
        (trees[structure_field] == require_structure) &
        trees[dbh_field].gt(min_dbh)
    )
    df = trees.loc[mask].copy()

    # 4: join to planting_spaces
    df = df.merge(
        planting_spaces[[ps_globalid, ps_status_field, ps_jur_field]],
        left_on=ps_key, right_on=ps_globalid,
        how="inner"
    )

    # 5: PS filters
    ps_mask = (
        (df[ps_status_field] == keep_ps_status) &
        (df[ps_jur_field] != exclude_jur)
    )
    df = df.loc[ps_mask]

    # 6: pare down + rename
    df = df[[id_field, "geometry"]]
    return gpd.GeoDataFrame(df, geometry="geometry", crs=trees.crs) \
        .rename(columns={id_field: out_id})


def canceled_work_orders(

    wo: gpd.GeoDataFrame,
    *,
    wo_type_field: str = "wotype",
    wo_cat_field: str = "wocategory",
    wo_status_field: str = "wostatus",
    allowed_types: Optional[list[str]] = None,
    allow_category: str = "Tree Planting",
    cancel_status: str = "Cancel",
    id_field: str = "objectid",
    out_id: str = "WOID"
) -> gpd.GeoDataFrame:
    """Filter wo's to cancelled planting jobs."""

    if allowed_types is None:
        allowed_types = [
            "Tree Plant-Park Tree",
            "Tree Plant-Street Tree",
            "Tree Plant-Street Tree Block"
        ]

    mask = (
        wo[wo_type_field].isin(allowed_types) &
        (wo[wo_cat_field] == allow_category) &
        (wo[wo_status_field] == cancel_status)
    )
    df = wo.loc[mask, [id_field, "geometry"]].copy()
    return df.rename(columns={id_field: out_id})


def clean_planting_spaces(
    ps: gpd.GeoDataFrame,
    *,
    status_field: str = "psstatus",
    keep_status: str = "Populated",
    jur_field: str = "jurisdiction",
    exclude_jur: str = "Private",
    id_field: str = "globalid",
    out_id: str = "PSID"
) -> gpd.GeoDataFrame:
    """Return populated planting spaces excluding private sites."""
    mask = ps[status_field] == keep_status
    if exclude_jur:
        mask &= (ps[jur_field] != exclude_jur)

    df = ps.loc[mask, [id_field, "geometry"]].copy()
    return df.rename(columns={id_field: out_id})


def clean_street_signs(
    gdf: gpd.GeoDataFrame,
    *,
    require_record_type: str = "Current",
    date_fields: Optional[list[str]] = None,
    int_fields: Optional[list[str]] = None,
    drop_suffixes: Optional[list[str]] = None,
    keep_fields: Optional[list[str]] = None
) -> gpd.GeoDataFrame:
    """Clean street sign records and drop any non-current entries."""
    df = gdf.copy()

    if date_fields is None:
        date_fields = ["order_completed_on_date", "sign_design_voided_on_date"]
    if int_fields is None:
        int_fields = ["distance_from_intersection"]
    if drop_suffixes is None:
        drop_suffixes = ["on_street_suffix",
                         "from_street_suffix",
                         "to_street_suffix"
                         ]
    if keep_fields is None:
        keep_fields = [
            "order_number", "record_type", "order_type", "borough",
            "on_street", "from_street", "side_of_street",
            "order_completed_on_date", "sign_code", "sign_description",
            "sign_size", "sign_location", "distance_from_intersection",
            "arrow_direction", "sheeting_type", "support",
            "to_street", "facing_direction", "sign_notes",
            "sign_design_voided_on_date"
        ]

    # 0) keep only Current orders
    df = df[df["record_type"].str.strip().str.title() == require_record_type]

    # 1) Parse dates
    for fld in date_fields:
        if fld in df:
            df[fld] = pd.to_datetime(df[fld], errors="coerce")

    # 2) Numeric cast
    for fld in int_fields:
        if fld in df:
            df[fld] = pd.to_numeric(df[fld], errors="coerce")

    # 3) Drop unused suffixes
    df = df.drop(columns=[c for c in drop_suffixes if c in df.columns],
                 errors="ignore")

    # 4) Subset to relevant columns + geometry
    final_cols = [c for c in keep_fields if c in df.columns] + ["geometry"]
    df = df[final_cols].copy()

    # 5) Clean up strings
    df["record_type"] = df["record_type"].str.strip().str.title()
    df["side_of_street"] = df["side_of_street"].str.strip().str.upper()
    df["arrow_direction"] = df["arrow_direction"].str.strip()
    df["sign_description"] = df["sign_description"].str.strip()

    return gpd.GeoDataFrame(df, geometry="geometry", crs=gdf.crs)
