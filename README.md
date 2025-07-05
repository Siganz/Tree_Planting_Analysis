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
