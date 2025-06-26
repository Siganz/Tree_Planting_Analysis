from pathlib import Path
import yaml

_CONSTANTS = None


def _load_constants():
    global _CONSTANTS
    if _CONSTANTS is None:
        const_path = Path(__file__).resolve().parents[2] / "config" / "constants.yml"
        with open(const_path) as f:
            _CONSTANTS = yaml.safe_load(f) or {}
    return _CONSTANTS


def get_constant(key, default=None):
    """Return constant value from config/constants.yml"""
    return _load_constants().get(key, default)

