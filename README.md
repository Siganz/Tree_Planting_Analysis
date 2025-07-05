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

3. Copy `config/user.example.yaml` to `config/user.yaml` and
   fill in your credentials. The `user.yaml` file is ignored by Git.

## Environment Setup

This project uses a simple pip-based workflow for development and code review.

**To install the required developer tools, run:**

pip install black flake8 isort pytest

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
