# Notes

### Downloading data
1. **Load configuration**  
   1. Read `config/config.yaml` to get:  
       - EPSG code for reprojection  
       - Output folder path  
       - Database enabled flag and connection details  
   2. Ensure the output folder exists or create it  

2. **Read data source list**  
   1. Open `config/data_sources.json`  
   2. Parse each entry’s `id`, `url`, and `source_type`  

3. **Initialize storage mode**  
   1. If database mode is enabled:  
       - Build the PostGIS connection URL  
       - Create the SQLAlchemy engine  
   2. If database mode is disabled:  
       - Define a fresh GeoPackage file in the output folder  
       - Remove any existing GeoPackage to start clean  

4. **Prepare HTTP session**  
   1. Instantiate a single `requests.Session()` for all downloads  

5. **Fetch each layer**  
   1. Loop through the parsed sources (track progress with a counter)  
   2. For an ArcGIS REST service:  
       - Retrieve its JSON metadata to get the native CRS  
       - Download its GeoJSON features  
       - Load into a GeoDataFrame, set the source CRS, then reproject  
   3. For an ArcGIS item (zipped File Geodatabase):  
       - Download and unzip to a temporary folder  
       - Locate the `.gdb` directory  
       - List all layers inside and read each into a GeoDataFrame  
       - Set CRS and reproject each one  

6. **Persist fetched data**  
   1. For each GeoDataFrame returned:  
       - If in database mode, write it to a PostGIS table  
       - Otherwise, append it as a layer in the GeoPackage  

7. **Cleanup**  
   1. Delete any temporary unzip folders used for GDB downloads  

8. **Final check**  
   1. In database mode, verify tables exist in PostGIS  
   2. In file mode, open the GeoPackage and confirm layers are present  

### Political Boundary
1. **List layers**
2. **Select layers**
    1. borough
    2. community_district
    3. council_district
    4. congressional_districts
    5. senate_districts
    6. assembly_districts
    7. community_tabulations
    9. neighborhood_tabulations
    10. census_tracts
    11. census_blocks
    12. zoning_districts
    13. commercial_districts
    14. special_districts
3. **Union layers**
4. **Output to geopackage or server db**
    1. political_boundaries

### Data Prep
1. **List layers**
2. **Select layers**
    1. curb
        1. select 
            1. sub_feature_code 222600
            2. sub_feature_code 222700
    2. 
    3.
    4.


### Sidewalk Creation
1. **List layers**
2. **Select layers**
    1. 

### Sidewalk Resolution
1. feature to point
2. spatial join w/ centerlines
3. join field
- This provides the sidewalks with the street they are on. This is so signs near the intersection can attach to the correct sidewalk. 
