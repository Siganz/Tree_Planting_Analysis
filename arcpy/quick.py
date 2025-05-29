import arcpy
import os

# Inputs
signs_fc = arcpy.GetParameterAsText(0)
sidewalks_fc = arcpy.GetParameterAsText(1)
centerlines_fc = arcpy.GetParameterAsText(2)

scratch = arcpy.env.scratchGDB
near_table = os.path.join(scratch, "signs_to_centerline_near")
filtered_sidewalks = os.path.join(scratch, "sidewalks_tagged")

# ── Step 1: Get closest centerline to each sign ──
arcpy.analysis.GenerateNearTable(
    in_features=signs_fc,
    near_features=centerlines_fc,
    out_table=near_table,
    search_radius="50 Feet",
    location="NO_LOCATION",
    angle="NO_ANGLE",
    closest="ALL",
    closest_count=1
)

# ── Step 2: Add geometry to centerlines (flow vector) ──
arcpy.management.AddGeometryAttributes(
    centerlines_fc,
    Geometry_Properties="LINE_START_MID_END"
)

# ── Step 3: Join vector coords onto signs ──
arcpy.management.JoinField(
    signs_fc, "OBJECTID",
    near_table, "IN_FID",
    ["NEAR_FID"]
)

arcpy.management.JoinField(
    signs_fc, "NEAR_FID",
    centerlines_fc, "OBJECTID",
    ["START_X", "START_Y", "END_X", "END_Y"]
)

# ── Step 4: Add sign_lr ──
arcpy.management.AddGeometryAttributes(signs_fc, "POINT_X_Y_Z_M")

arcpy.management.AddField(signs_fc, "sign_lr", "TEXT", field_length=1)
arcpy.management.CalculateField(
    signs_fc, "sign_lr",
    expression=(
        '"L" if ((!END_X! - !START_X!) * (!POINT_Y! - !START_Y!) - '
        '(!END_Y! - !START_Y!) * (!POINT_X! - !START_X!)) > 0 else "R"'
    ),
    expression_type="PYTHON3"
)

# ── Step 5: Do same for sidewalks ──
arcpy.management.AddGeometryAttributes(
    sidewalks_fc, "CENTROID_INSIDE"
)
arcpy.management.JoinField(
    sidewalks_fc, "OBJECTID",
    centerlines_fc, "OBJECTID",
    ["START_X", "START_Y", "END_X", "END_Y"]
)

arcpy.management.AddField(sidewalks_fc, "sidewalk_lr", "TEXT", field_length=1)
arcpy.management.CalculateField(
    sidewalks_fc, "sidewalk_lr",
    expression=(
        '"L" if ((!END_X! - !START_X!) * (!INSIDE_Y! - !START_Y!) - '
        '(!END_Y! - !START_Y!) * (!INSIDE_X! - !START_X!)) > 0 else "R"'
    ),
    expression_type="PYTHON3"
)

# ── Step 6: Filter sidewalks by side, run final Near by chunks ──
# GenerateNearTable doesn’t support side-by-side filtering directly, so you’ll have to:
# - create two layers: sidewalks_L and sidewalks_R
# - loop over signs_fc with layer filter (sign_lr = 'L') and only run Near to matching sidewalk_lr

# Not shown here to keep this short, but can do:
# arcpy.MakeFeatureLayer with where_clause="sidewalk_lr = 'L'" and same for signs_fc
