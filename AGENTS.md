# AGENTS.md

## 🗺️ Project Scope
- **Primary code**: `src/stp/`
- **Configuration & templates**: `config/`
- **Data inputs**: `Data/` (read-only)
- **.gitignore** excludes hidden/data files — never commit those.

## 🧪 Testing Guidelines
1. **Run unit tests** only on pure-Python modules under `tests/`  
   ```bash
   pytest tests/ --ignore=tests/gis_* --maxfail=1 -q
   ```
2. **Skip** any tests or code paths that import GDAL, Fiona, Rasterio, or other GIS-native libs.  
3. **Fail fast**: abort on the first error.

## 🧑‍💻 Style
- **Indentation**: 4 spaces only  
- **No trailing whitespace** on any line  
- **Import order**:
  1. Standard library  
  2. Third-party  
  3. Local (`src/stp/...`)  
- **Max line length**: 79 characters

## 🧑‍💻 Code Style & Documentation
- Every public function and class **must** have a descriptive docstring.  
- Use inline `#` comments sparingly, only for non-obvious logic.  
- **Main workflows** (CLI entrypoints, high-level scripts) should use `logger.info/debug/error` for status and errors.  
- **Helper modules** should raise exceptions on error rather than logging.

## 🤖 Agent Workflow
1. **Detect changed files** in a PR; limit actions to:
   - `src/stp/`  
   - `tests/`  
   - `config/`  

2. Lint **all changed or newly created Python files** using:
    ```bash
    flake8 {changed_or_new_file.py} --max-line-length=79
   ```
3. **Run tests**:  
   ```bash
   pytest tests/ --ignore=tests/gis_* --maxfail=1 -q
   ```
4. **If** any lint or test step fails → **abort** and report errors; do **not** propose a PR draft.  
5. **If** all checks pass → generate the PR diff with clear rationale for each change.

## 📋 PR & Commit Conventions
- **Branch**: `codex/<short-description>`  
- **PR Title**: `[<area>] <brief description>`  
- **Commit Title**: same as PR Title  
- **Commit Body**:
  1. **What** changed  
  2. **Why** it changed  
  3. **How** to test  
- **Do not** commit secrets or `config/secrets.yaml`.
