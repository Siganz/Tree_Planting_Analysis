"""Tree-related cleaning routines."""

from typing import Optional

import geopandas as gpd

MIN_DBH = 0.01


def clean_trees_basic(
    trees: gpd.GeoDataFrame,
    *,
    structure_field: str = "tpstructure",
    require_structure: str = "Full",
    id_field: str = "objectid",
    out_id: str = "TreeID",
) -> gpd.GeoDataFrame:
    """Return trees with full structure."""
    df = trees.loc[
        trees[structure_field] == require_structure, [id_field, "geometry"]
    ].copy()
    return df.rename(columns={id_field: out_id})


def clean_trees_advanced(
    trees: gpd.GeoDataFrame,
    planting_spaces: gpd.GeoDataFrame,
    *,
    condition_field: str = "tpcondition",
    drop_conditions: Optional[list[str]] = None,
    structure_field: str = "tpstructure",
    require_structure: str = "Full",
    dbh_field: str = "dbh",
    min_dbh: float = MIN_DBH,
    ps_key: str = "plantingspaceglobalid",
    ps_globalid: str = "globalid",
    ps_status_field: str = "psstatus",
    keep_ps_status: str = "Populated",
    ps_jur_field: str = "jurisdiction",
    exclude_jur: str = "Private",
    id_field: str = "objectid",
    out_id: str = "TreeID",
) -> gpd.GeoDataFrame:
    """Return cleaned trees joined to planting spaces."""
    if drop_conditions is None:
        drop_conditions = ["Unknown", "Dead"]
    mask = (
        ~trees[condition_field].isin(drop_conditions)
        & (trees[structure_field] == require_structure)
        & trees[dbh_field].gt(min_dbh)
    )
    df = trees.loc[mask].copy()
    df = df.merge(
        planting_spaces[[ps_globalid, ps_status_field, ps_jur_field]],
        left_on=ps_key,
        right_on=ps_globalid,
        how="inner",
    )
    ps_mask = (
        (df[ps_status_field] == keep_ps_status)
        & (df[ps_jur_field] != exclude_jur)
    )
    df = df.loc[ps_mask]
    df = df[[id_field, "geometry"]]
    return gpd.GeoDataFrame(df, geometry="geometry", crs=trees.crs).rename(
        columns={id_field: out_id}
    )


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
    out_id: str = "WOID",
) -> gpd.GeoDataFrame:
    """Filter work orders to cancelled planting jobs."""
    if allowed_types is None:
        allowed_types = [
            "Tree Plant-Park Tree",
            "Tree Plant-Street Tree",
            "Tree Plant-Street Tree Block",
        ]
    mask = (
        wo[wo_type_field].isin(allowed_types)
        & (wo[wo_cat_field] == allow_category)
        & (wo[wo_status_field] == cancel_status)
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
    out_id: str = "PSID",
) -> gpd.GeoDataFrame:
    """Return populated planting spaces excluding private sites."""
    mask = ps[status_field] == keep_status
    if exclude_jur:
        mask &= ps[jur_field] != exclude_jur
    df = ps.loc[mask, [id_field, "geometry"]].copy()
    return df.rename(columns={id_field: out_id})
