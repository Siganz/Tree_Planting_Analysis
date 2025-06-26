# AGENTS.md

## 🗺️ Project Scope

* **Primary code** lives in `scripts/`
* **Configs/templates** in `config/` (`config.example.yml`).
* **Data inputs** live under `Data/` (gpkg, table) but agent **should not** modify raw data.
* **Ignore** in `.gitignore` will show all hidden files. Most importantly data, because we don't need data on the github. Locally, these files will be created, just never pushed to github. Keep that in mind. 

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
