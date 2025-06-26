# AGENTS.md

## 🗺️ Project Scope

* Primary code: `scripts/`
* Configs/templates: `config/`
* Data inputs: `Data/` (read-only)
* `.gitignore` excludes hidden/data files—never commit those.

## 🧪 Testing Guidelines

* GIS-native libraries (GDAL, Fiona, Rasterio) are **not** present in this environment.
* **Skip or stub** any tests or code paths requiring GIS-native functionality.
* Only run tests on pure-Python modules.

## 🚀 Environment Setup

* Dependencies are pre-installed in the Codex container.
* Use local `env/environment.yml` (and/or `env/requirements.txt`) for full GIS workflows outside Codex.

## 🛠️ Workflows & Validation

* **Testing:** Run pytest (maxfail=1, warnings off).
* **Linting:** Use flake8; enforce PEP8 and max line length 79.

## 🧑‍💻 Style

* 4-space indentation
* No trailing whitespace
* Imports: stdlib → third-party → local
* Max line length: 79

## 📋 PR/Commit

* Branch: `codex/<short-desc>`
* PR Title: `[<area>] <desc>`
* Commit body: what/why/how to test
* Never commit secrets/config.yml

## 🤖 Agent Behavior

1. Scan `scripts/` for context before edits.
2. Run lint/tests before proposing PRs.
3. Present diffs with clear rationale.

---
