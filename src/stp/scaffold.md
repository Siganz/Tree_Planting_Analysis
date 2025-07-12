# Scaffold.md: Tree Planting Analysis Pipeline Overview

This document outlines the high-level workflow for the STP (Spatial Tabular Pipeline) GIS project, originally built in ArcPy/ModelBuilder and now converted to pure Python (using GeoPandas for ops like buffers/unions/clips). The focus is NYC tree planting analysis, but it's designed for flexibility (e.g., toggle steps for other cities via config edits). We use a unified YAML config to drive the pipeline dynamically, with Docker for automatic PostGIS setup (spatial DB storage for efficient queries/filters).

## 1. Define Configuration
Configuration is centralized for ease—edit files to customize sources, ops, filters, and params without changing code. This replaces a "locked" pipeline with variable/user-defined flows (e.g., nest ops in YAML for reordering/toggling).

- **root/config/workflow.yaml**: Main unified config (combines sources, prep ops, filters, and final steps).
  - Data sources from open data portals (e.g., Socrata/ArcGIS REST).
  - Includes URL, type/format, schema, filter parameters (e.g., Socrata $where queries).
  - Nested ops/steps for processing (e.g., copy → select → buffer), with descriptions, enabled toggles, inputs/outputs.
  - Users can fill out or override (e.g., add local paths for offline use).
  - For reusing a feature class multiple times (e.g., curb_cut in different filters): Reference the same output_layer in steps—no duplication needed. If mutable (changes needed without overwriting), nest a 'copy' op first. If non-mutable download, use local_path fallback in sources section.
  - Example snippet (from our merged version):
    ```yaml
    data:  # Top-level for all datasets (renamed from 'data_id' for clarity)
        trees:
            sources:  # Fetch details
                type: "json"
                source_type: "socrata"
                format: "json"
                url: "https://data.cityofnewyork.us/resource/hn5i-inap.json"
                schema: "political"
                filter: "SITE_TYPE = 'Tree Site' AND CONDITION NOT IN ('Dead','Removed','Stump')"
                to_layer: "trees_raw"
                enabled: true
            prep_ops:  # Nested processing
                description: "Existing tree locations to avoid"
                enabled: true
                steps:
                    - op: copy
                    input: "trees_raw"  # References the source's to_layer
                    output: "trees_copy"
                    - op: xy_to_point
                    output: "trees_1"
                    - op: buffer
                    distance: 25
                    output: "trees_ready"

        nyzd:  # Another dataset bundle
            sources:
            # ... (URL/type/filter)
            prep_ops:
            # ... (steps like copy/select)
    ```

- **root/config/defaults.yaml**: Stores default parameters for tools/ops (e.g., EPSG codes, limits). Optional but useful for globals; can be loaded into pipeline.py and overridden in workflow.yaml if needed.
  - Example:
    ```yaml
    epsg:
      default: 4326
      nysp: 2263
    limits:
      socrata: 50000
      arcgis_default_max_records: 1000
    validation:
      layer_name_max_length: 60
      min_dbh: 0.01
    ```

- **root/config/user.yaml**: User-specific overrides (e.g., API keys, batch params, DB creds). Loads defaults.yaml if none specified. With variable pipelines, this is key for personalization (e.g., change Socrata batch size).
  - Example for DB/Docker:
    ```yaml
    db:
      user: 'admin'
      pass: 'admin'
      host: 'localhost'
      port: 5432
      db_name: 'tree_pipeline'
    api:
      socrata_key: 'your_key_here'  # If needed for throttled APIs
      batch_size: 50000  # Override defaults never above 50000, if above revert to 50,000
    ```

## 2. Download Sources & Create Mutable DB 
Primary goal: Fetch and prep NYC-relevant data for tree planting (e.g., trees, hydrants, sidewalks) from open sources. Variable for other cities (edit workflow.yaml URLs/filters). Downloads via fetchers/ (Socrata/ArcGIS REST handlers in STP tools), with API keys/batch params from user.yaml (e.g., batch to avoid limits on big datasets like census blocks).

- Sources located in workflow.yaml 'sources' section (merged from old sources.json).
- Sources can be from anywhere, but default to Socrata and ArcGIS REST.
  - Requires API key/parameters (e.g., batch size/combining for large fetches) from user.yaml.
- Storage: Use Docker to automatically install/setup a DB with PostgreSQL/PostGIS for spatial efficiency (queries/filters on layers like zoning districts).
  - Docker auto-creates the environment (isolated, portable—run `docker compose up -d` from docker-compose.yml).
  - Load creds from user.yaml (e.g., user: 'admin', pass: 'admin', host: 'localhost', port: 5432).
  - Connect: `engine = create_engine('postgresql://admin:admin@localhost:5432/tree_pipeline')`.
  - Load data: After download, `gdf.to_postgis('trees_raw', engine, if_exists='replace')` (GeoPandas handles conversion to spatial tables).
  - Why PostGIS? Faster for ops (e.g., SQL filters during select) than files; fallback to GPKG if needed.
- Prep: Run nested steps from workflow.yaml 'prep_ops' (e.g., copy → xy_to_point → buffer). Outputs saved as new tables/layers.
- Final clip/big scripts: Handled in workflow.yaml sections (nested steps for union/clip/points generation, then nostanding/rank/curb).

## 3. Initiate Pipeline
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
