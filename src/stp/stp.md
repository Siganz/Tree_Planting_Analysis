# STP – Spatial / Tabular Pipeline

`src/stp` is a lightweight toolkit for fetching raw spatial / tabular data,
cleaning it, and persisting it to GeoPackage or PostGIS.  
Everything is pure-Python, built on GeoPandas, Shapely and SQLAlchemy.

---

## Folder structure

```
![alt text](image.png)
stp/
│
├── cleaning/        ← cleaning steps for specific datasets
│   ├── address.py
│   ├── trees.py
│   └── **init**.py
│
├── fetchers/        ← source-specific download helpers
│   ├── arcgis.py         # ArcGIS REST → GeoJSON/Parquet
│   ├── csv.py            # Plain CSV files (HTTP/local)
│   ├── gdb.py            # FileGDB via ogr2ogr
│   ├── geojson.py        # Arbitrary GeoJSON endpoints
│   ├── gpkg.py           # Remote GeoPackage layers
│   ├── socrata.py        # Socrata Open Data API
│   └── **init**.py
│
├── inventory/       ← schema inspection & export utilities
│   ├── export.py         # dump layer → CSV/Markdown schema
│   ├── gpkg.py           # field inventory for GeoPackage
│   ├── postgis.py        # field inventory for PostGIS
│   └── **init**.py
│
├── metadata/        ← read / write layer-level metadata
│   ├── csv.py            # side-car CSV metadata files
│   ├── db.py             # PostGIS / SQLite layer comments
│   └── **init**.py
│
├── scripts/         ← one-off CLI entry points
│   └── download_utils.py # `python -m stp.scripts.download_utils`
│
├── storage/         ← persistence back-ends
│   ├── db\_storage.py     # PostGIS via SQLAlchemy
│   ├── file\_storage.py   # GeoPackage / Shapefile
│   └── **init**.py
│
└── (root modules)   ← orchestration & shared helpers
├── config\_loader.py
├── data\_cleaning.py
├── download.py
├── fields\_inventory.py
├── http\_client.py
├── settings.py
├── table.py
└── **init**.py

```

---

## Top-level module cheat-sheet

| Module | Purpose |
|--------|---------|
| **config_loader.py** | Read YAML/ENV configuration & expose `get_setting`, `get_constant`. |
| **settings.py** | Hard-coded fall-backs (NYSP EPSG 2263, default filenames, etc.). |
| **download.py** | “Orchestrator” – loops through every fetcher listed in config and drops raw files into `Data/raw/`. |
| **http_client.py** | Thin `requests.Session` wrapper with retry & back-off. |
| **data_cleaning.py** | Pipeline runner – re-projects, trims fields, fixes datatypes using functions from `cleaning/`. |
| **fields_inventory.py** | Generates a schema report (dtype, null %, sample) for any GeoDataFrame or DB layer. |
| **table.py** | Helpers to convert between CSV ↔ GeoJSON ↔ GeoPackage with consistent field ordering. |

---

## How the pieces fit

```

fetchers/        →  Data/raw/\*.geojson / .csv
│
▼
cleaning/         GeoDataFrame in EPSG:2263
│
▼
storage/          PostGIS (db\_storage)  or  GeoPackage (file\_storage)
│
▼
inventory/        Optional schema dump / metadata write-back

````

---

### Quickstart

```bash
# 1) install deps
pip install -r requirements.txt   # add psycopg2-binary for PostGIS

# 2) pull all configured layers
python -m stp.download

# 3) clean & normalise
python -m stp.data_cleaning

# 4) inspect schema (optional)
python -m stp.fields_inventory Data/clean/addresses.gpkg
````

That’s it!
Drop this `README_stp.md` into `src/stp/` to give new contributors an instant
map of the toolkit.
