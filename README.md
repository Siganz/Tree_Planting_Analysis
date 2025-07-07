# Street Tree Planting Analysis (STP)

Scripts and tools for downloading, processing, and analyzing New York City street tree and sidewalk data.

---

## Table of Contents

* [Installation](#installation)
* [Environment Setup](#environment-setup)
* [Configuration](#configuration)
* [Folder Structure](#folder-structure)
* [Contributing](#contributing)
* [License](#license)

---

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/shawnganznyc/Street_Tree_Planting_Analysis.git
   cd Street_Tree_Planting_Analysis
   ```

2. **Install dependencies**
pip install -r requirements.txt

## Configuration

1. **Edit configuration files:**

   * `config/defaults.yaml` — project-wide constants (safe to commit)
   * `config/user.yaml` — user-specific secrets/overrides (do **NOT** commit)

2. **On first use:**

   * Copy `config/user.example.yaml` to `config/user.yaml` and fill in any required secrets (e.g. Socrata app token).
   * Ensure `config/user.yaml` is listed in `.gitignore`.

---

## Folder Structure

```
config/      - Configuration files (defaults, user secrets)
src/stp/     - Main Python package (cleaning, fetchers, storage, etc.)
Data/        - Downloaded/generated data (not tracked in version control)
tests/       - Unit and integration tests
```

---

## Scope

1. Read user parameters
2. Download files
3. Create GIS assets if specified/possible
4. Clean
   * Read user settings per item to figure out what fields to keep. 
5. Manipulate
   * Shapes undergo geoprocessing functions
      * User specified options
         * ex: Buffer, 20 ft. 
   * Pipeline functions
      * union
      * clip
      * merge
      * spatial join
      * custom operations
6. Combine
7. Output
   * Number of potential trees in the area. 

# Primary Scope

1. Read established parameters
2. Download files from arcgis/nyc opendata
3. Convert json into geojson point/polygons
4. Clean files of unecessary fields
5. Apply buffers, filters, custom scripts. 
6. Create a sidewalk polyline using polygon buffer
   - Copy non mutable sidewalk polyline
7. Merge all polygons where plantings cannot occur. 
8. Clip do not plant locations with sidewalk polyline. 
9. Use non mutable sidewalk polyline to use for traffic signs / parking rules
   - Build no parking zones
      - Classify no parking into bins: 
         - No Parking
         - No Standing
            - No Standing Taxi
            - No Standing Truck Loading
            - No Standing (something else, forgot)
   - Build sidewalk vehicle parking times into each sidewalk 
   - Build mta no bus locations/rules
10. Generate potential planting locations
11. Join potential planting location with sidewalk information
12. Done.

# Current Goal
- Functioning python pipeline
   - Pipeline already developed on arcpy.
- User parameter control
   - Allow user to manipulate variables/parameters. 
      - Atm the original project use parameters and variables are somewhat set. 
- Automatic pipeline based on geography
   - All inputs need to be faithful to the pipeline, otherwise errors will occur
   - Template settings for all major cities? 

## Contributing

Pull requests and issues are welcome. Please open an issue to discuss major changes before submitting a PR.

---

## License

This project is open-source. See `LICENSE` for details.

---

**Tip:**
All user secrets and API keys go in `config/user.yaml` (never committed).
Project settings and defaults live in `config/defaults.yaml`.

---

Let me know if you want any sections expanded or customized for your onboarding workflow.
