# AGENTS.md

## ✏️ Code Style Guide

This project enforces basic Python style conventions across `src/stp/`.

---

### 🔹 Formatting Rules

- **Indentation**: 4 spaces  
- **Line length**: max 79 characters  
- **No trailing whitespace**  
- **Blank lines**:  
  - 2 between top-level functions and classes  
  - 1 between method definitions inside classes  

---

### 🔹 Import Order

1. **Standard library**
2. **Third-party**
3. **Local modules** (`src/stp/...`)

Use `isort` or arrange manually to match.

---

### 🔹 Docstrings

- Required on all **public functions** and **classes**
- Use triple double quotes (`"""docstring"""`)
- Be concise and descriptive

---

### 🔹 Comments

- Use inline `#` comments sparingly — only for **non-obvious logic**
- Avoid restating what the code already expresses clearly

---

### 🔹 Enforcement

You can check for style issues using:

```bash
flake8 src/stp/ --max-line-length=79
pylint src/stp/
```

---

### ❌ Exclusions

These folders are not checked by linters:

- `.venv/`
- `Data/`
- `config/`
- `tests/gis_*`

---

This file focuses only on style. Testing, CI, and agents are optional layers you can add later.
