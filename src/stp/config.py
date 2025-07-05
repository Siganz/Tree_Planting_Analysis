"""
config.py — Project configuration loader

This module centralizes access to application settings. It loads
constants from a single source (constants.yaml) at import time and
provides:

  • get_constant(name: str) -> Any
      Fetch a value by key from constants.yaml (raises KeyError
      if missing).

  • get_project_setting(key: str,
                        default: Optional[Any] = None) -> Any
      Look up a dot-delimited setting in the user’s config.yaml,
      falling back to constants.yaml or the provided default.
"""
from pathlib import Path
from typing import Any, Optional

import yaml

_CFG_DIR = Path(__file__).resolve().parents[2] / 'config'
_USER_CFG_PATH = _CFG_DIR / 'config.yaml'
_CONSTS_PATH = _CFG_DIR / 'constants.yaml'

# Load constants once
with open(_CONSTS_PATH, encoding='utf-8') as _f:
    _CONSTANTS: dict[str, Any] = yaml.safe_load(_f)


def get_constant(name: str) -> Any:
    """Fetch `name` from constants.yaml; KeyError if missing."""
    try:
        return _CONSTANTS[name]
    except KeyError as e:
        raise KeyError(f"Missing constant '{name}' in {_CONSTS_PATH}") from e


def get_setting(key: str, default: Optional[Any] = None) -> Any:
    """Return a setting from user config or fall back to constants.yaml.

    Args:
        key (str): Dot-delimited path into the YAML (e.g. 'db.host').
        default (Any, optional): Value to return if neither is set.

    Returns:
        Any: The user override, or the constant, or `default`.
    """
    # 1) Try user config
    if _USER_CFG_PATH.exists():
        with open(_USER_CFG_PATH, encoding='utf-8') as _f:
            user_cfg = yaml.safe_load(_f) or {}
        value: Any = user_cfg
        for part in key.split('.'):
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                value = None
                break
        if value is not None:
            return value

    # 2) Fall back to constants.yaml
    try:
        return get_constant(key)
    except KeyError:
        return default
