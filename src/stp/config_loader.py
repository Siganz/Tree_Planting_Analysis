"""Helpers for loading project configuration and constants."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

import yaml

_CONFIG_DIR = Path(__file__).resolve().parents[2] / "config"
_SETTINGS_PATH = _CONFIG_DIR / "settings.yaml"
_DEFAULTS_PATH = _CONFIG_DIR / "defaults.yaml"


def _load_yaml(path: Path) -> Mapping[str, Any]:
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


_SETTINGS = _load_yaml(_SETTINGS_PATH)
_CONSTANTS = _load_yaml(_DEFAULTS_PATH)


def _get_by_path(data: Mapping[str, Any], key: str) -> Any:
    cur: Any = data
    for part in key.split("."):
        if isinstance(cur, Mapping) and part in cur:
            cur = cur[part]
        else:
            return None
    return cur


def get_setting(key: str, default: Any = None) -> Any:
    """Return a project setting from ``settings.yaml``."""
    val = _get_by_path(_SETTINGS, key)
    return default if val is None else val


def get_constant(key: str, default: Any = None) -> Any:
    """Return a constant value from ``defaults.yaml``."""
    val = _get_by_path(_CONSTANTS, key)
    return default if val is None else val
