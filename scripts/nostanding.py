import os
import pandas as pd
import arcpy

arcpy.env.overwriteOutput = True
scratch = arcpy.env.scratchGDB

def classify(raw):
    txt = str(raw).upper()
    if "NO STANDING" in txt:     return "NSTAND"
    if "NO PARKING"  in txt:     return "NPARK"
    if "HMP"         in txt:     return "HMP"
    if "TAXI" in txt or "HOTEL" in txt or "LOADING" in txt or "PASSENGER" in txt:
                                return "CURBSIDE"
    return "OTHER"

def load_filter(csv_path, desc_f, side_f):
    df = pd.read_csv(csv_path)
    
    # normalize N/S/E/W
    df[side_f] = (df[side_f]
                  .astype(str).str.strip()
                  .str.upper().str[0]
                  .where(lambda s: s.isin(list("NSEW"))))
    df = df[df[side_f].notna()]

    # keep only our keywords
    keep = "NO STANDING|NO PARKING|HMP|TAXI|HOTEL|LOADING|PASSENGER"
    df = df[df[desc_f].str.upper().str.contains(keep, na=False)]

    # valid coords
    df = df[pd.to_numeric(df["sign_x_coord"], "coerce").notna()]
    df = df[pd.to_numeric(df["sign_y_coord"], "coerce").notna()]

    # dedupe on 1-ft grid
    df["x_r"] = df["sign_x_coord"].round(1)
    df["y_r"] = df["sign_y_coord"].round(1)
    df = df.drop_duplicates(subset=["x_r", "y_r"]).reset_index(drop=True)

    # parse arrow glyphs
    def _pa(s):
        s = str(s).upper()
        if "<->" in s:
            return "<->"
        elif "-->" in s or "->" in s:
            return "->"
        elif "<--" in s or "<-" in s:
            return "<-"
    df["parsed_arrow"] = df[desc_f].apply(_pa)
    df = df[df["parsed_arrow"].notna()]

    return df

# helper that classifies the segment side
def segment_compass(seg_geom, sign_pt):
    dx = seg_geom.centroid.X - sign_pt.centroid.X
    dy = seg_geom.centroid.Y - sign_pt.centroid.Y
    if abs(dx) >= abs(dy):                       # horizontal dominates or ties
        return "east" if dx > 0 else "west"
    else:                                        # vertical dominates
        return "north" if dy > 0 else "south"

# ── 0. Params ───────────────────────────────────────────────────────────────
# 0: csv_path, 1: sw_fc, 2: cen_fc, 3: out_fc, 4: desc_f, 5: side_f, 6: shift_ft
csv_path, sw_fc, cen_fc, out_fc, desc_f, side_f, shift_ft = [
    arcpy.GetParameterAsText(i) for i in range(7)
]
shift_ft = float(shift_ft)

# ── 0.1 Copy & integrate centerlines (don’t mutate source)───────────────────
cen_work = os.path.join(scratch, "cen_work")
arcpy.management.CopyFeatures(cen_fc, cen_work)
arcpy.management.Integrate(cen_work, "0.01 Feet")

# ── 1.  CSV → point feature class  ─────────────────────────────────────────
df = load_filter(csv_path, desc_f, side_f)
df["sign_type"] = df[desc_f].map(classify)
df["jid"] = df.index
tmp_csv = os.path.join(scratch, "clean_signs.csv")
df.to_csv(tmp_csv, index=False,
          columns=["jid", "sign_x_coord", "sign_y_coord", side_f, "parsed_arrow","sign_type"])
arcpy.AddMessage(f"Cleaned signs CSV → {tmp_csv}")

sr = arcpy.SpatialReference(2263)          # NY State Plane Feet
signs = os.path.join(scratch, "signs_pts")
arcpy.management.XYTableToPoint(tmp_csv, signs,
                                "sign_x_coord", "sign_y_coord",
                                coordinate_system=sr)
arcpy.AddMessage(f"Signs → point FC: {signs}")

# ── 2.  Curb offset  ──────────────────────────────────────────────────────
signs_shifted = os.path.join(scratch, "signs_shifted")
arcpy.management.CopyFeatures(signs, signs_shifted)

with arcpy.da.UpdateCursor(signs_shifted, ["SHAPE@", side_f]) as cur:
    for shp, sd in cur:
        dx, dy = {"N": (0,  shift_ft),
                  "S": (0, -shift_ft),
                  "E": ( shift_ft, 0),
                  "W": (-shift_ft, 0)}.get((sd or "").upper(), (0, 0))
        pt = shp.centroid
        new_pt = arcpy.PointGeometry(arcpy.Point(pt.X + dx, pt.Y + dy), sr)
        cur.updateRow([new_pt, sd])

arcpy.AddMessage("↔️  Shifted signs off original location.")

# ── 3.  Build working sidewalk copy  ──────────────────────────────────────
arcpy.env.overwriteOutput = True
sw_work = os.path.join(scratch, "sw_work")
if arcpy.Exists(sw_work):
    arcpy.Delete_management(sw_work)
arcpy.management.CopyFeatures(sw_fc, sw_work)
arcpy.AddMessage(f"Copied sidewalks → {sw_work}")

# ── 4.  Snap curb‑shifted signs to their sidewalk  ────────────────────────
signs_snapped_sw = os.path.join(scratch, "signs_snapped_sw")
arcpy.management.CopyFeatures(signs_shifted, signs_snapped_sw)

near_sidewalk = os.path.join(scratch, "near_sidewalk")
arcpy.analysis.GenerateNearTable(signs_snapped_sw, sw_work,
                                 near_sidewalk, search_radius="60 Feet",
                                 closest="CLOSEST")

arcpy.management.JoinField(signs_snapped_sw,      # target
                           "OBJECTID",            # sign OID
                           near_sidewalk,         # near table
                           "IN_FID",              # join key
                           ["NEAR_FID"])          # adds curb sidewalk OID
arcpy.AddMessage("📌  Joined NEAR_FID onto curb‑shifted signs.")

# lookup:  sidewalk OID  →  geometry
sw_geom = {oid: g for oid, g in arcpy.da.SearchCursor(sw_work, ["OID@", "SHAPE@"])}

with arcpy.da.UpdateCursor(signs_snapped_sw, ["SHAPE@", "NEAR_FID"]) as cur:
    for shp, nid in cur:
        seg = sw_geom.get(nid)
        if seg:
            meas = seg.measureOnLine(shp.centroid)
            cur.updateRow([seg.positionAlongLine(meas), nid])

arcpy.AddMessage(f"Snapped signs → sidewalks: {signs_snapped_sw}")

# ── 4.2  Filter out signs that never snapped to a sidewalk ────────────────

# A.  signs whose NEAR_FID is NULL  →  sign_errors
sign_errors = os.path.join(scratch, "sign_errors")
arcpy.analysis.Select(signs_snapped_sw, sign_errors, "NEAR_FID IS NULL")

# B.  signs we want to ignore (e.g. sign_type = 'NPARK')  →  sign_skip
sign_skip = os.path.join(scratch, "sign_skip")
arcpy.analysis.Select(signs_snapped_sw, sign_skip, "sign_type = 'NPARK'")

# C.  delete both kinds from the working sign layer
with arcpy.da.UpdateCursor(signs_snapped_sw,
        ["NEAR_FID", "sign_type"]) as cur:

    for nid, stype in cur:
        if nid is None or stype == "NPARK":
            cur.deleteRow()

cnt_orphan = int(arcpy.management.GetCount(sign_errors)[0])
cnt_skip   = int(arcpy.management.GetCount(sign_skip)[0])

arcpy.AddMessage(f"🛈  {cnt_orphan} orphans → sign_errors; "
                 f"{cnt_skip} NPARK signs → sign_skip.")

# ------------------------------------------------------------
# 4.  Keep only sidewalks that have at least one matched sign
# ------------------------------------------------------------
# 4‑A  sid list from NEAR_FID
ids = {oid for oid, in arcpy.da.SearchCursor(signs_snapped_sw, ["NEAR_FID"])
        if oid is not None}

if not ids:
    arcpy.AddWarning("No sidewalks matched any sign within 60 ft — nothing to process.")
    raise SystemExit()

id_sql = f"OBJECTID IN ({','.join(map(str, ids))})"

sw_work_has_sign = os.path.join(scratch, "sw_work_has_sign")
arcpy.analysis.Select(sw_work, sw_work_has_sign, id_sql)

arcpy.AddMessage(f"Sidewalks with signs → {sw_work_has_sign} ({len(ids)})")

# join the side code from sidewalk layer onto the sign layer
arcpy.management.JoinField(signs_snapped_sw,       # target
                           "NEAR_FID",             # key on sign
                           sw_work_has_sign,       # source sidewalks
                           "OBJECTID",
                           [side_f])               # e.g. SIDE_CODE

# add a compass field and populate it
arcpy.management.AddField(signs_snapped_sw, "COMPASS", "TEXT", field_length=5)

arrow_to_compass = {
    "E": {"<-": "north", "->": "south"},
    "W": {"<-": "south", "->": "north"},
    "N": {"<-": "west",  "->": "east"},
    "S": {"<-": "east",  "->": "west"},
}

with arcpy.da.UpdateCursor(signs_snapped_sw,
        [side_f, "parsed_arrow", "COMPASS"]) as cur:

    for curb, arr, comp in cur:
        curb = (curb or "").strip().upper()
        arr  = (arr  or "").strip()

        if arr == "<->":
            comp = "both"
        else:
            comp = arrow_to_compass.get(curb, {}).get(arr)

        cur.updateRow([curb, arr, comp])

# ------------------------------------------------------------
# 5.  Erase a ±1.5 ft window around each sign (buffer‑erase)
# ------------------------------------------------------------

# 5‑A  buffer the signs once
sign_buf = os.path.join(scratch, "sign_buf")
arcpy.analysis.Buffer(signs_snapped_sw, sign_buf, "1.5 Feet",
                      dissolve_option="NONE")

# Erase a ±1.5 ft window around each sign
sw_split_raw = os.path.join(scratch, "sw_split_raw")
arcpy.analysis.PairwiseErase(sw_work_has_sign, sign_buf, sw_split_raw)
arcpy.AddMessage(f"Erased 3 ft gaps at signs → {sw_split_raw}")

# explode multipart to singlepart
sw_split = os.path.join(scratch, "sw_split")              # final working copy
arcpy.management.MultipartToSinglepart(sw_split_raw, sw_split)

# drop zero‑length slivers
sliver_sql = "SHAPE_Length < 0.05"          # adjust threshold if needed
arcpy.management.MakeFeatureLayer(sw_split, "split_lyr", sliver_sql)
if int(arcpy.management.GetCount("split_lyr")[0]) > 0:
    arcpy.management.DeleteFeatures("split_lyr")
arcpy.management.Delete("split_lyr")

# ------------------------------------------------------------
# 6.  Flag before / after / both via COMPASS logic
# ------------------------------------------------------------

# --- sign geometry lookup (needed inside the cursor) ----------
sign_geom = {oid: geom for oid, geom
             in arcpy.da.SearchCursor(signs_snapped_sw,
                                      ["OBJECTID", "SHAPE@"])}

# 1) ONE‑TO‑MANY spatial join: every segment ↔ every sign ≤ 2 ft
sw_join = os.path.join(scratch, "sw_split_joined")
arcpy.analysis.SpatialJoin(
    target_features   = sw_split,          # exploded single‑part segments
    join_features     = signs_snapped_sw,  # snapped signs (with COMPASS)
    out_feature_class = sw_join,
    join_operation    = "JOIN_ONE_TO_MANY",
    match_option      = "WITHIN_A_DISTANCE",
    search_radius     = "2 Feet"
)

# rename join keys for clarity
arcpy.management.AlterField(sw_join, "TARGET_FID", new_field_name="SEG_ID")
arcpy.management.AlterField(sw_join, "JOIN_FID",   new_field_name="SIGN_OID")
arcpy.management.JoinField(sw_join,          # target = sw_join rows
                           "SIGN_OID",       # key in sw_join
                           signs_snapped_sw, # source signs
                           "OBJECTID",       # key in signs
                           ["sign_type"])    # field(s) to copy

# add the flag field *before* the cursor
arcpy.management.AddField(sw_join, "no_stand", "SHORT")

# 2) row‑by‑row flag
with arcpy.da.UpdateCursor(
        sw_join,
        ["SEG_ID", "SIGN_OID", "COMPASS", "no_stand", "SHAPE@"]) as cur:

    for seg_id, soid, comp, flag, seg in cur:
        if comp == "both":
            flag = 1
        else:
            sign_pt  = sign_geom.get(soid)
            seg_side = segment_compass(seg, sign_pt)
            flag     = int(seg_side == comp) if seg_side else 0
        cur.updateRow([seg_id, soid, comp, flag, seg])

# 3) collapse duplicates: MAX(no_stand) per segment
stat_tbl = os.path.join(scratch, "seg_flag_stat")
arcpy.analysis.Statistics(
        sw_join, stat_tbl,
        [["no_stand", "MAX"]],
        case_field="SEG_ID")

arcpy.management.AlterField(stat_tbl, "MAX_no_stand",
                            new_field_name="no_stand")

# choose "MIN_SIGN_TYPE" = the alphabetically first type for that segment
type_tbl = os.path.join(scratch, "seg_type_stat")
arcpy.analysis.Statistics(
    sw_join, type_tbl,
    [["sign_type", "MIN"]],          # MIN, MAX, or COUNT
    case_field="SEG_ID")

arcpy.management.AlterField(type_tbl, "MIN_sign_type",
                            new_field_name="sign_type")

# join both flag + type back onto sw_split
arcpy.management.JoinField(sw_split, "OBJECTID",
                           stat_tbl,  "SEG_ID", ["no_stand"])
arcpy.management.JoinField(sw_split, "OBJECTID",
                           type_tbl,  "SEG_ID", ["sign_type"])

# 4) join the final flag back to the single‑part sidewalk layer
#    remove any placeholder no_stand first
if "no_stand" in [f.name for f in arcpy.ListFields(sw_split)]:
    arcpy.management.DeleteField(sw_split, ["no_stand"])

arcpy.management.JoinField(sw_split,          # target = segments
                           "OBJECTID",        # key in sw_split
                           stat_tbl,          # source table
                           "SEG_ID",          # key in stats table
                           ["no_stand"])

arcpy.AddMessage("✅  Segments flagged via COMPASS logic")

# ------------------------------------------------------------
# 8.  Clean up & export
# ------------------------------------------------------------
arcpy.management.CopyFeatures(sw_split, out_fc)     # overwriteOutput should be True
arcpy.AddMessage(f"🎉  Final no‑standing layer → {out_fc}")