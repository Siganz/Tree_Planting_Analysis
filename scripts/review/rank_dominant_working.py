import arcpy
from pathlib import Path
import pandas as pd
from collections import defaultdict

arcpy.ImportToolbox(r"D:\ArcGIS\Projects\Street_Tree_Planting_Analysis\Street_Tree_Planting_Analysis.atbx", "stp")

def generate_initial_points(line_fc, spacing, work_gdb):
    """Copy input lines, then create and rank an initial set of points."""
    lines_working = str(work_gdb / "lines_working")
    if arcpy.Exists(lines_working):
        arcpy.management.Delete(lines_working)
    
    arcpy.management.CopyFeatures(str(line_fc), lines_working)

    pts = str(work_gdb / "pts_0")
    arcpy.stp.generatepoints(lines_working, str(spacing), pts)
    arcpy.stp.addrankfields(pts, lines_working)

    return lines_working, pts

def identify_non_conflicting_points(pts, spacing, work_gdb):
    """Remove points that intersect within 'spacing' feet of each other."""
    pts_work = str(work_gdb / "pts_0_working")
    arcpy.management.CopyFeatures(pts, pts_work)

    conflicts_fc = str(work_gdb / "potential_conflicts")
    arcpy.analysis.SpatialJoin(
        target_features=pts_work,
        join_features=pts_work,
        out_feature_class=conflicts_fc,
        join_operation="JOIN_ONE_TO_MANY",
        match_option="INTERSECT",
        search_radius=f"{spacing} Feet"
    )

    # Filter out self-joins so only overlapping points remain

    true_conflicts = str(work_gdb / "true_conflicts")
    arcpy.management.MakeFeatureLayer(conflicts_fc, "conflicts_lyr")
    arcpy.management.SelectLayerByAttribute("conflicts_lyr", "NEW_SELECTION", '"PARENT_OID" <> "PARENT_OID_1"')
    arcpy.management.CopyFeatures("conflicts_lyr", true_conflicts)

    conflict_ids = {row[0] for row in arcpy.da.SearchCursor(true_conflicts, ["TARGET_FID"])}

    # Remove points whose OID appears in the conflict table
    good_boys_fc = str(work_gdb / "pts_0_cleaned")
    with arcpy.da.UpdateCursor(pts_work, ["OBJECTID"]) as cursor:
        for row in cursor:
            if row[0] in conflict_ids:
                cursor.deleteRow()

    arcpy.management.CopyFeatures(pts_work, good_boys_fc)
    return good_boys_fc

def resolve_conflicts_iteratively(pts, lines_working, spacing, buffer_dist, work_gdb, max_iterations=3):
    """Iteratively buffer and erase lines to remove conflicting planting points."""
    iter_n = 0
    line_suppress_map = defaultdict(list)

    while True:
        iter_n += 1
        if iter_n > max_iterations:
            arcpy.AddWarning("Max iterations reached.")
            break
        
        line_suppress_map = defaultdict(list)

        near_tbl = str(work_gdb / f"near_{iter_n}")
        arcpy.analysis.GenerateNearTable(
            pts, pts, near_tbl, f"{buffer_dist} Feet", "NO_LOCATION",
            closest="ALL", method="PLANAR"
        )  # produces pairwise distances between points

        if int(arcpy.management.GetCount(near_tbl)[0]) == 0:
            break

        df = pd.DataFrame(arcpy.da.TableToNumPyArray(near_tbl, ["IN_FID", "NEAR_FID"]))
        df = df[df.IN_FID < df.NEAR_FID]

        rank = {}
        with arcpy.da.SearchCursor(pts, ["OID@", "PARENT_LEN", "PARENT_FID"]) as cur:
            for oid, ln_len, ln_fid in cur:
                rank[oid] = (ln_len, ln_fid)

        winners, losers = set(), set()
        for _, row in df.iterrows():
            i, j = int(row.IN_FID), int(row.NEAR_FID)
            if i not in rank or j not in rank or rank[i][1] == rank[j][1]:
                continue
            r_i, r_j = rank[i][0], rank[j][0]
            if r_i > r_j or (r_i == r_j and i < j):
                winners.add(i)
                losers.add(j)
                line_suppress_map[rank[j][1]].append(i)
            else:
                winners.add(j)
                losers.add(i)
                line_suppress_map[rank[i][1]].append(j)

        if not winners:
            break

        # Points to buffer are the losers grouped by parent line
        suppression_pts = list({oid for pts in line_suppress_map.values() for oid in pts})
        existing_oids = {row[0] for row in arcpy.da.SearchCursor(pts, ["OID@"])}
        suppression_pts = [oid for oid in suppression_pts if oid in existing_oids]

        if not suppression_pts:
            continue

        suppression_pt_layer = arcpy.management.MakeFeatureLayer(pts, "suppression_pts")[0]
        oid_field = arcpy.Describe(suppression_pt_layer).OIDFieldName
        arcpy.management.SelectLayerByAttribute(
            suppression_pt_layer, "NEW_SELECTION",
            f"{oid_field} IN ({','.join(map(str, suppression_pts))})"
        )

        # Defensive check before buffering
        count = int(arcpy.management.GetCount(suppression_pt_layer)[0])
        arcpy.AddMessage(f"🧪 Suppression point layer count: {count}")
        if count == 0:
            arcpy.AddMessage("⚠️ No suppression points selected — skipping regeneration.")
            continue  # skip this iteration

        # Now it's safe to buffer
        buffer_fc = work_gdb / f"iter_{iter_n}_winner_buffers"
        arcpy.analysis.PairwiseBuffer(suppression_pt_layer, str(buffer_fc), f"{buffer_dist - 0.01} Feet", dissolve_option="ALL")

        losing_lines = list(line_suppress_map.keys())
        losing_line_layer = arcpy.management.MakeFeatureLayer(lines_working, "losing_losing_line_layer")[0]
        oid_field = arcpy.Describe(losing_line_layer).OIDFieldName
        arcpy.management.SelectLayerByAttribute(
            losing_line_layer, "NEW_SELECTION", f"{oid_field} IN ({','.join(map(str, losing_lines))})"
        )

        arcpy.AddMessage(f"🧪 Trying to erase these lines: {losing_lines[:5]}... (total: {len(losing_lines)})")

        count = int(arcpy.management.GetCount(str(losing_line_layer))[0])
        arcpy.AddMessage(f"📊 Selected lines for erase: {count}")
        if count == 0:
            arcpy.AddWarning("⚠️ No losing lines selected — skipping erase this round.")
            continue

        # Optional geometry repair
        arcpy.management.RepairGeometry(str(buffer_fc), "DELETE_NULL")

        # Run erase
        trimmed_losing_lines = work_gdb / f"iter_{iter_n}_trimmed_losing_lines"
        arcpy.analysis.PairwiseErase(losing_line_layer, str(buffer_fc), str(trimmed_losing_lines))

        # Select survivor lines (NOT in losing_lines)
        survivor_lines = work_gdb / f"iter_{iter_n}_survivor_lines"
        arcpy.management.MakeFeatureLayer(lines_working, "lines_working_lyr")
        arcpy.management.SelectLayerByAttribute(
            "lines_working_lyr", "NEW_SELECTION",
            f"{oid_field} NOT IN ({','.join(map(str, losing_lines))})"
        )
        arcpy.management.CopyFeatures("lines_working_lyr", str(survivor_lines))

        # Merge survivors + trimmed losers
        merged_lines = work_gdb / f"iter_{iter_n}_merged_lines"
        arcpy.management.Merge([str(survivor_lines), str(trimmed_losing_lines)], str(merged_lines))

        # Filter out final lines under X feet before generating points
        min_line_length = 3
        lines_filtered = str(work_gdb / f"iter_{iter_n}_filtered_lines")

        # Create in-memory layer from merged result
        filtered_layer = arcpy.management.MakeFeatureLayer(str(merged_lines), f"merged_lines_lyr_{iter_n}")[0]

        # Select only lines that meet minimum length
        arcpy.management.SelectLayerByAttribute(
            filtered_layer, "NEW_SELECTION",
            f"Shape_Length >= {min_line_length}"
        )

        # Save filtered version to new feature class
        arcpy.management.CopyFeatures(filtered_layer, lines_filtered)

        # Set for next round
        lines_working = lines_filtered

        # Step: Regenerate points
        pts = str(work_gdb / f"pts_{iter_n}_regenerated")
        arcpy.stp.generatepoints(lines_working, str(spacing), pts)
        arcpy.stp.addrankfields(pts, lines_working)

    return None, None, iter_n, lines_working

def rank_dominant_prune(line_fc: str, out_pts_fc: str, final_lines_fc: str, spacing: float, buffer_dist: float) -> None:
    """High level prune workflow used by the ArcGIS tool."""
    work_gdb = Path(arcpy.env.scratchGDB)
    arcpy.env.workspace = str(work_gdb)
    arcpy.env.overwriteOutput = True

    # Step 1: Generate working copy of input lines and initial points
    lines_working, pts = generate_initial_points(line_fc, spacing, work_gdb)

    # Step 2: Run all pruning — this mutates lines_working
    _, _, _, final_lines = resolve_conflicts_iteratively(
        pts, lines_working, spacing, buffer_dist, work_gdb
    )

    # Step 3: Generate final planting points from clean geometry
    arcpy.stp.generatepoints(str(final_lines), str(spacing), out_pts_fc)
    arcpy.AddMessage(f"🌳 Final planting points generated from trimmed geometry: {out_pts_fc}")

    # Step 4: Generate final plantable sidewalk from clean geometry
    arcpy.management.CopyFeatures(final_lines, final_lines_fc)
    arcpy.AddMessage(f"🗂 Final pruned sidewalk geometry saved to: {final_lines_fc}")

# ArcGIS Tool Entry
if __name__ == "__main__":
    line_fc = arcpy.GetParameterAsText(0)
    out_pts_fc = arcpy.GetParameterAsText(1)
    final_lines_fc = arcpy.GetParameterAsText(2)
    spacing = float(arcpy.GetParameterAsText(3))
    buffer_dist = float(arcpy.GetParameterAsText(4))

    rank_dominant_prune(line_fc, out_pts_fc, final_lines_fc, spacing, buffer_dist)
