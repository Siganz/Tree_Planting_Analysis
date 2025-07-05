"""Configuration helpers: load constants and project settings."""
from pathlib import Path
import yaml

_CONSTANTS = None


def _load_constants():
    """Load constants.yaml once and cache the parsed dictionary."""
    global _CONSTANTS
    if _CONSTANTS is None:
        const_path = (
            Path(__file__).resolve().parents[2]
            / "config"
            / "constants.yaml"
        )
        with open(const_path, encoding="utf-8") as f:
            _CONSTANTS = yaml.safe_load(f) or {}
    return _CONSTANTS


def get_constant(key, default=None):
    """Return constant value from config/constants.yaml."""
    return _load_constants().get(key, default)


def get_project_setting(key, default=None):
    """Return setting value: first try user config, then constants.yaml
    fallback."""
    cfg_path = (
        Path(__file__).resolve().parents[2]
        / "config"
        / "config.yaml"
    )
    raw_cfg = {}
    if cfg_path.exists():
        with open(cfg_path, encoding="utf-8") as f:
            raw_cfg = yaml.safe_load(f) or {}
    parts = key.split('.')
    value = raw_cfg
    for part in parts:
        if isinstance(value, dict) and part in value:
            value = value[part]
        else:
            value = None
            break
    if value is None:
        consts = _load_constants()
        value = consts
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                value = default
                break
    return value