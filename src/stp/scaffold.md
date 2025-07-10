# Original Arcpy Workflow

## Info
This was the original workflow created for the project in arcpy. There are some specific order, but the end result was a bunch of layers that will be utilized as either information to join to the potential tree points created at the end of the projects pipeline or information to clip from the sidewalks. 

1. Drink some coffee
2. Download & prep sources
   2.1 Define source paths & queries:
    - trees
        - json

    - work_orders
        - json

    - planting_spaces
        - json

    - street_sign
        - json

    - hydrants
        - json

    - green_infrastructure
        - json

    - subway_lines
        - shapefile

    - borough
        - shapefile

    - community_districts
        - shapefile

    - council_districts
        - shapefile

    - congressional_districts
        - shapefile

    - senate_districts
        - shapefile

    - assembly_districts
        - shapefile

    - community_tabulations
        - shapefile

    - neighborhood_tabulations
        - shapefile

    - census_tracts
        - shapefile

    - census_blocks
        - shapefile

    - zoning_districts
        - shapefile

    - commercial_districts
        - shapefile

    - special_purpose_districts
        - shapefile

    - pluto
        - shapefile

    - street_center
        - shapefile

    - curb
        - shapefile

    - curb_cut
        - shapefile

    - sidewalk
        - shapefile

3. Download & Convert JSON → GeoJSON / in-geodatabase exports
    - Data sources: 
        - Socrata
        - ArcGIS REST 
    - Data is initially stored in ./data 
    * files are stored in a gpkg in ./data/gpkg

4. Data Cleaning
    - 

5. Preliminary Operations
   3.1 ExportFeatures(Online_NYZD → NYZD)
   3.2 PairwiseBuffer(NYZD → NYZD_Buffer, 20 ft)
   3.3 ExportFeatures(BK_Vaults → BK_Vaults_2)
   3.4 PairwiseBuffer(BK_Vaults_2 → BK_Vaults_Buffer, 20 ft)
   3.5 ExportFeatures(STP_Apps_Vaults → DOT_Vault_ExportFeatures)
   3.6 PairwiseBuffer(DOT_Vault_ExportFeatures → DOT_Vault_Buffer, 20 ft)
   3.7 ExportFeatures(ConEd_Transformer_Vault → ConEd_Transformer_Vault)
   3.8 PairwiseBuffer(ConEd_Transformer_Vault → ConEd_Transformer_Buffer, 20 ft)
   3.9 ExportFeatures(DEP_GI_Assets → DEP_GI_Assets)
   3.10 PairwiseBuffer(DEP_GI_Assets → DEP_GI_Assets_Buffer, 20 ft)

4. Copy & select raw features
   4.1 CopyFeatures(SIDEWALK → SIDEWALK_2)
   4.2 CopyFeatures(HVI_CensusTracts_v2013 → HVI_CensusTracts_v2013_Copy)
   4.3 CopyFeatures(Curb_Cuts_Intersections_2 → CURB_CUT_CopyFeatures)
   4.4 Select(CURB_CUT_CopyFeatures → Curb_Cuts_Intersections, where SUB_FEATURE_CODE=222700)
   4.5 PairwiseBuffer(Curb_Cuts_Intersections → Curb_Cuts_Intersection_Buffer, 30 ft)
   4.6 CopyFeatures(Subway_Lines → Subway_Lines_2)
   4.7 PairwiseBuffer(Subway_Lines_2 → Subway_Lines_Buffer, 80 ft)

5. Convert CSV → points
   5.1 ExportTable(Workorders.csv → Workorders)
   5.2 XYTableToPoint(Workorders → Workorders_XYTableToPoint)
   5.3 PairwiseBuffer(Workorders_XYTableToPoint → WorkOrders_Buffer, 25 ft)
   5.4 ExportTable(TreeandSite.csv → TreenSite)
   5.5 XYTableToPoint(TreenSite → TreenSite_XYTableToPoint)
   5.6 PairwiseBuffer(TreenSite_XYTableToPoint → TreeAndSite_Buffer, 25 ft)

6. Clean & prep shrub layer
   6.1 CopyFeatures(Grass_Shrub_ExportFeatures → Grass_Shrub)
   6.2 DeleteField(Grass_Shrub, ["Id", "gridcode"])
   6.3 AddField("Pit_Type", TEXT, length=10)
   6.4 CalculateField(Pit_Type = "EP/LP")

7. Clean & prep HVI tracts
   7.1 CopyFeatures(FHNR_Datasets_HVI_CensusTracts → HVI_CensusTracts_v2013_CopyFeatures)
   7.2 DeleteField(HVI_CensusTracts_v2013_CopyFeatures, [...lots of fields...])
   7.3 AlterField("QUINTILES" → "HVI_CT_2013")

8. Union political & HVI boundaries
   8.1 Union([
         Political_Boundary,
         HVI_CensusTracts_v2013_CopyFeatures_2,
         NYCDOHMH_HVI_CensusTracts_2018_Clip,
         NYCDOHMH_HVI_CensusTracts_2023,
         NYCDOHMH_HVI_NeighborhoodTabulationAreas_2018,
         NYCDOHMH_HVI_NeighborhoodTabulationAreas_2023,
         NYCDCP_Borough_Boundaries_Water_Included,
         NYCDCP_Borough_Boundaries
       ] → Political_Boundary_Final)
   8.2 DeleteField(Political_Boundary_Final, [all FID_* fields])

9. Further buffers & selections
   9.1 PairwiseBuffer(Curb_Cuts_Intersections → Curb_Cuts_Intersection_20ft, 20 ft)
   9.2 Select(Street_Centerline WHERE L_LOW_HN <> '' → Street_Centerline_Select)
   9.3 SimplifyLine(Street_Centerline_Select → Street_Centerli_SimplifyLine, POINT_REMOVE, 1 ft)
   9.4 FeatureVerticesToPoints(Street_Centerli_SimplifyLine → Street_Vertices_Points)
   9.5 PairwiseBuffer(Street_Vertices_Points → Street_Vertice_Buffer, 40 ft)

10. Hydrant proximity & cleanup
   10.1 Near(DEP_Hydrants → Sidewalk_Pluto, radius=10 ft, location)
   10.2 MoveStreetSigns(Hydrants_Near → Hydrants_Corrected)
   10.3 PairwiseBuffer(Hydrants_Corrected → DEP_Hydrants_PairwiseBuffer, 3 ft)

11. Driveway curb-cut processing
    11.1 Select(CURB_CUT_CopyFeatures WHERE SUB_FEATURE_CODE=222600 → Curb_Cuts_Driveways)
    11.2 CurbCuts(input=Curb_Cuts_Driveways, extension=7, buffer=15 → Curb_Cuts_Driveways_Buffer)

12. Vault union & cleanup
    12.1 Union([BK_Vaults_Buffer, DOT_Vault_Buffer] → Vaults)
    12.2 DeleteField(Vaults, [a long list of original fields])
    12.3 AddField("Vaults", LONG)
    12.4 CalculateField(Vaults = 1)
    12.5 (Placeholder) Union(… → Output_Feature_Class)

13. Final buffer
    13.1 PairwiseBuffer(Curb_Cuts_Intersections → Curb_Cuts_Intersection_10ft, 10 ft)
