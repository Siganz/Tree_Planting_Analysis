# 📋 TODO – Street Tree Planting Analysis

### 🔧 Infrastructure
- [ ] Add optional PortableGit setup instructions for users without system Git
- [X] Create `data/` folder inside project for SQLite storage
- [ ] Create declaritive config layer

### 📂 Data & Layers
- [ ] Refactor `layers.json` to support `sqlite` as primary backend
- [ ] Flesh out `layers.json` with all required datasets for project (e.g., political boundaries, sidewalks, HVI, vaults, etc.)
- [ ] Mark which layers are external (URLs) vs. local shapefiles

### 🔄 Automation
- [ ] Create Python script to parse `layers.json` and auto-download any missing datasets
- [ ] Add flag for overwriting vs skipping if files already exist
- [ ] Add support for GeoJSON → GeoPackage/SQLite conversion on import

### 🧪 Testing & Validation
- [ ] Validate that downloaded datasets match expected schema
- [ ] Add lightweight test runner to confirm layer load and spatial projection

### 🗃️ Database Expansion (optional)
- [ ] Define SQLite schema layout for project
- [ ] Create optional PostgreSQL bootstrapping fallback using `init_postgres.json`

