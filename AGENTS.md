# AGENTS.md

## 🗺️ Project Scope

* Primary code: `src/stp`
* Configs/templates: `config/`
* Data inputs: `Data/` (read-only)
* `.gitignore` excludes hidden/data files—never commit those.

## 🧪 Testing Guidelines

* GIS-native libraries (GDAL, Fiona, Rasterio) are **not** present in this environment.
* **Skip or stub** any tests or code paths requiring GIS-native functionality.
* Only run tests on pure-Python modules.

## 🧑‍💻 Style

* 4-space indentation
* No trailing whitespace
* Imports: stdlib → third-party → local
* Max line length: 79

## 🧑‍💻 Code Style and Documentation

- All public functions and classes must have clear, descriptive docstrings.
- Add inline `# comments` to explain non-obvious or complex code sections.
- Logging (`logger.info`, etc.) should be used in main workflow scripts to track progress and issues.
- Helpers should avoid logging except for critical errors; prefer raising exceptions for error handling.

## 📋 PR/Commit

* Branch: `codex/<short-desc>`
* PR Title: `[<area>] <desc>`
* Commit body: what/why/how to test
* Never commit secrets/config.yml

## 🤖 Agent Behavior

1. Run lint/tests before proposing PRs.
3. Present diffs with clear rationale.

---
