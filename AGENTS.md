# AGENTS.md

## 🗺️ Project Scope

* **Primary code** lives in `scripts/`
* **Configs/templates** in `config/` (`config.example.yml`)
* **Data inputs** live under `Data/` (GPKG, tables), but agents **must not** modify raw data.
* **Ignore** entries in `.gitignore` include hidden files and data folders—these are generated locally and should never be committed.

## 🧪 Testing Guidelines

* The test environment does **not** include GIS-native libraries (GDAL, Fiona, Rasterio) or `gdal-config`.
* **Skip** or **stub** any tests or code paths that import or call GIS functions:

  * Wrap or guard imports:

    ```python
    try:
        from osgeo import gdal
    except ImportError:
        gdal = None
    ```
  * Mark tests for GIS-dependent modules with `@pytest.mark.skip` or conditional skip logic:

    ```python
    import pytest

    try:
        import fiona
    except ImportError:
        pytest.skip("GIS libraries not available in test env", allow_module_level=True)
    ```
* Pure-Python modules (e.g., data transformers, API clients) should be tested normally.

---

*Agents should use this doc to understand project boundaries and testing constraints.*

## 🚀 Setup

*Dependencies are installed via the Codex “Setup script” box; agent does not need to install anything here.*

## 🛠️ Workflows & Validation

### Testing

```bash
pytest --maxfail=1 --disable-warnings -q
```

### Linting (PEP8 + project rules)

```bash
flake8 scripts/ --max-line-length=79
```

## 🧑‍💻 Type & Style Guidelines

* Use **4-space** indentation
* No **trailing whitespace**
* Import order: **stdlib** → **third-party** → **local**
* Max line length: **79** characters

## 📋 PR/Commit Guidelines

* **Branch naming**: `codex/<short-description>`
* **PR Title**: `[<area>] Brief description`

  * e.g., `[scripts] add support for new EPSG`
* **Commit message body**:

  1. What changed and why
  2. How to test
* **Do not** commit real secrets or `config/config.yml`

## 🧭 Agent Behavior

1. **Explore** `scripts/` for context before editing.
2. **Run** lint & tests **before** proposing a PR.
3. **Present** diffs with clear headings and concise rationale.
