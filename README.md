# Street Tree Planting Analysis (STP)

A collection of scripts for downloading and analyzing New York City street tree and related infrastructure data.

## Table of Contents

- [Installation](#installation)
- [Environment Setup](#environment-setup)
- [Folder Structure](#folder-structure)
- [Contributing](#contributing)
- [License](#license)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/shawnganznyc/Street_Tree_Planting_Analysis.git
cd Street_Tree_Planting_Analysis
```

2. Create the Conda environment and install dependencies:

```bash
conda env create -f env/environment.yml
conda activate stp
pip install -r env/requirements.txt
```

## Environment Setup

The project uses a hybrid Conda and pip workflow.
Key environment files are located in `env/`:

- `environment.yml` – base Conda environment specification.
- `requirements.txt` – additional Python packages installed via `pip`.

For a step-by-step guide see [`env/_environment_readme`](env/_environment_readme).

## Folder Structure

```
config/   - Configuration templates and data source lists
docs/     - Project notes and miscellaneous documentation
env/      - Conda environment files and package requirements
scripts/  - Main Python scripts and helper modules
Data/     - Downloaded data (not tracked in version control)
```

## Contributing

Pull requests and issues are welcome. Please open an issue to discuss your ideas before submitting a PR.

## License

This project is provided under an open-source license. See `LICENSE` (to be added) for details.
