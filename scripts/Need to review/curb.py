import arcpy
import math
import os

def get_dominant_segment_angle(polyline_geom):
    max_len = 0
    best_angle = 0
    for i in range(polyline_geom.partCount):
        part = polyline_geom.getPart(i)
        prev_point = None
        for pt in part:
            if not pt: continue
            if prev_point:
                dx = pt.X - prev_point.X
                dy = pt.Y - prev_point.Y
                seg_len = math.hypot(dx, dy)
                if seg_len > max_len:
                    max_len = seg_len
                    best_angle = math.atan2(dy, dx)
            prev_point = pt
    return best_angle

def script_tool(input_feature_class, output_feature_class, extension_distance, buffer_width):
    """Fast rectangular polygon generator around lines with extension."""
    arcpy.env.overwriteOutput = True
    spatial_ref = arcpy.Describe(input_feature_class).spatialReference

    arcpy.CreateFeatureclass_management(
        out_path=os.path.dirname(output_feature_class),
        out_name=os.path.basename(output_feature_class),
        geometry_type='POLYGON',
        spatial_reference=spatial_ref
    )

    with arcpy.da.SearchCursor(input_feature_class, ['SHAPE@']) as sCursor, \
         arcpy.da.InsertCursor(output_feature_class, ['SHAPE@']) as iCursor:

        for polyline_geom in sCursor:
            line = polyline_geom[0]
            if line.pointCount < 2:
                continue  # Skip degenerate lines

            angle = get_dominant_segment_angle(line)
            start = line.firstPoint
            end = line.lastPoint

            # Extend line ends
            sx = start.X - extension_distance * math.cos(angle)
            sy = start.Y - extension_distance * math.sin(angle)
            ex = end.X + extension_distance * math.cos(angle)
            ey = end.Y + extension_distance * math.sin(angle)

            # Buffer offset
            dx = (buffer_width / 2.0) * math.sin(angle)
            dy = (buffer_width / 2.0) * math.cos(angle)

            points = [
                arcpy.Point(sx - dx, sy + dy),
                arcpy.Point(ex - dx, ey + dy),
                arcpy.Point(ex + dx, ey - dy),
                arcpy.Point(sx + dx, sy - dy)
            ]

            polygon = arcpy.Polygon(arcpy.Array(points), spatial_ref)
            iCursor.insertRow([polygon])

    return output_feature_class

# ─── Entry Point ───
if __name__ == "__main__":
    input_feature_class = arcpy.GetParameterAsText(0)
    output_feature_class = arcpy.GetParameterAsText(1)
    extension_distance = float(arcpy.GetParameterAsText(2))
    buffer_width = float(arcpy.GetParameterAsText(3))

    result = script_tool(input_feature_class, output_feature_class, extension_distance, buffer_width)
    arcpy.SetParameterAsText(1, result)
