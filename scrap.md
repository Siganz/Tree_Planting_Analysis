# To Use / How To Use

## No Planting Areas / Locations to clip sidewalk

- NYZD  
  - Description: Zoning districts where planting is prohibited  
  - Filters: `"ZONE_DIST" IN ('M1','M2','M3','IG','IH')`  
  - Operations  
    - Operation a: CopyFeatures  
      - Output: `nyzd_copy`  
    - Operation b: Select  
      - Params: filter above  
      - Output: `nyzd_ready`

- DEP_GI_Assets  
  - Description: Green infrastructure assets to avoid  
  - Filters: None  
  - Operations  
    - Operation a: CopyFeatures  
      - Output: `dep_gi_assets_copy`  
    - Operation b: Buffer  
      - Params: distance = 20 Feet  
      - Output: `dep_gi_assets_ready`

- Sidewalk  
  - Description: Raw sidewalk polygons, split for different logic  
  - Filters: None  
  - Operations  
    - Operation a: CopyFeatures  
      - Output: `sidewalk_copy`  
    - Operation b: Polygon→Polyline  
      - Params: input = `sidewalk_copy`  
      - Output: `sidewalk_1`  
    - Operation c: Split immutable/mutable  
      - Params: input = `sidewalk_1`  
      - Outputs: `sidewalk_immutable_ready`, `sidewalk_mutable_ready`

- Curb_Cuts  
  - Description: Sidewalk curb-cut intersections  
  - Filters: `SUB_FEATURE_CODE = 222700`  
  - Operations  
    - Operation a: CopyFeatures  
      - Output: `curb_cuts_copy`  
    - Operation b: Select  
      - Params: filter above  
      - Output: `curb_cuts_1`  
    - Operation c: Buffer  
      - Params: input = `curb_cuts_1`, distance = 30 Feet  
      - Output: `curb_cuts_ready`

- Subway_Lines  
  - Description: Subway buffers to exclude planting near tracks  
  - Filters: None  
  - Operations  
    - Operation a: CopyFeatures  
      - Output: `subway_lines_copy`  
    - Operation b: Buffer  
      - Params: distance = 80 Feet  
      - Output: `subway_lines_ready`

- Workorders  
  - Description: Active DOT work orders  
  - Filters: `STATUS <> 'Cancelled'`  
  - Operations  
    - Operation a: CopyFeatures (ExportTable/Select)  
      - Output: `workorders_copy`  
    - Operation b: XYTableToPoint  
      - Params: input = `workorders_copy`  
      - Output: `workorders_1`  
    - Operation c: Buffer  
      - Params: input = `workorders_1`, distance = 25 Feet  
      - Output: `workorders_ready`

- TreeandSite  
  - Description: Existing tree locations to avoid  
  - Filters: `SITE_TYPE = 'Tree Site' AND CONDITION NOT IN ('Dead','Removed','Stump')`  
  - Operations  
    - Operation a: CopyFeatures (ExportTable/Select)  
      - Output: `treeandsite_copy`  
    - Operation b: XYTableToPoint  
      - Params: input = `treeandsite_copy`  
      - Output: `treeandsite_1`  
    - Operation c: Buffer  
      - Params: input = `treeandsite_1`, distance = 25 Feet  
      - Output: `treeandsite_ready`

- Grass_Shrub  
  - Description: 2017 land-use raster converted to shrub/grass polygons  
  - Filters: None  
  - Operations  
    - Operation a: CopyFeatures (Copy Raster)  
      - Output: `grass_shrub_copy`  
    - Operation b: RasterToPolygon_conversion  
      - Params: simplify = NO_SIMPLIFY  
      - Output: `grass_shrub_1`  
    - Operation c: DeleteField  
      - Params: fields = `["gridcode","Id"]`  
      - Output: `grass_shrub_ready`

- Political_Boundary  
  - Description: Union of all political boundaries for spatial join  
  - Filters: None  
  - Operations  
    - Operation a: CopyFeatures  
      - Output: `political_boundary_copy`  
    - Operation b: Union_analysis  
      - Params: inputs = borough, community boards, council, senate, assembly, NTA, tracts  
      - Output: `political_boundary_1`  
    - Operation c: DeleteField  
      - Params: fields = all `FID_*`  
      - Output: `political_boundary_ready`

- Street_Centerline  
  - Description: Simplify street geometry and buffer vertices  
  - Filters: `L_LOW_HN IS NOT NULL`  
  - Operations  
    - Operation a: CopyFeatures  
      - Output: `street_centerline_copy`  
    - Operation b: SimplifyLine_cartography  
      - Params: method = POINT_REMOVE, tolerance = 1 Feet  
      - Output: `street_centerline_1`  
    - Operation c: FeatureVerticesToPoints  
      - Params: input = `street_centerline_1`  
      - Output: `street_centerline_2`  
    - Operation d: Buffer  
      - Params: input = `street_centerline_2`, distance = 40 Feet  
      - Output: `street_centerline_ready`

- DEP_Hydrants  
  - Description: Hydrant proximity adjustments  
  - Filters: None  
  - Operations  
    - Operation a: CopyFeatures  
      - Output: `dep_hydrants_copy`  
    - Operation b: GenerateNearTable  
      - Params: distance = 10 Feet  
      - Output: `dep_hydrants_1`  
    - Operation c: MoveStreetSigns (custom)  
      - Params: as defined in script  
      - Output: `dep_hydrants_2`  
    - Operation d: Buffer  
      - Params: input = `dep_hydrants_2`, distance = 3 Feet  
      - Output: `dep_hydrants_ready`

- Curb_Cuts_Driveways  
  - Description: Driveway curb cuts to exclude planting  
  - Filters: `SUB_FEATURE_CODE = 222600`  
  - Operations  
    - Operation a: CopyFeatures  
      - Output: `curb_cuts_driveways_copy`  
    - Operation b: Select  
      - Params: filter above  
      - Output: `curb_cuts_driveways_1`  
    - Operation c: Buffer  
      - Params: input = `curb_cuts_driveways_1`, distance = 15 Feet  
      - Output: `curb_cuts_driveways_ready`

## Final first step

- Final Clip  
  - Description: Compute allowable planting points within clipped sidewalk  
  - Filters: None  
  - Operations  
    - Operation a: CopyFeatures (non-mutable backup)  
      - Params: input = `sidewalk_mutable_ready`  
      - Output: `sidewalk_mutable_backup`  
    - Operation b: Union no-plant zones  
      - Params: inputs = nyzd_ready, dep_gi_assets_ready, curb_cuts_ready, subway_lines_ready, workorders_ready, treeandsite_ready, grass_shrub_ready  
      - Output: `no_plant_zones_union`  
    - Operation c: Clip_analysis  
      - Params: input = `sidewalk_mutable_ready`, clip_features = `no_plant_zones_union`  
      - Output: `sidewalk_availability_ready`  
    - Operation d: Create planting points  
      - Params: method = CreateFishnet or custom  
      - Output: `plant_pts_1`  
    - Operation e: SpatialJoin  
      - Params: target = `plant_pts_1`, join_features = `sidewalk_availability_ready`  
      - Output: `plant_pts_ready`
