"""Load configuration defaults and user overrides, merging deeply where needed."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

import yaml
from dotenv import load_dotenv

load_dotenv()  # Loads from .env by default

def load_user_config():
    return {
        "api_key": os.getenv("API_KEY"),
        "db_user": os.getenv("DB_USER"),
        "db_pass": os.getenv("DB_PASS"),
    }



# In-memory config stores, filled by load_config()
_defaults: Dict[str, Any] = {}
_overrides: Dict[str, Any] = {}


def _deep_get(mapping: Dict[str, Any], keys: list[str]) -> Any:
    """Safely walk through nested dictionaries using a list of keys.

    Args:
        mapping (Dict[str, Any]): The starting dictionary.
        keys (list[str]): A list of keys representing the path to access.

    Returns:
        Any: The nested value if the path exists, otherwise None.
    """
    current = mapping
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _merge(base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively deep-merge two dictionaries.

    - For any key where both base and update,
        have dicts, merge them recursively.
    - Otherwise, the update's value replaces the base's value.
    """
    result = dict(base)  # Shallow copy base so we don't mutate it
    for key, val in update.items():
        # Only recurse if both base and update have dicts at this key
        if (
            key in result
            and isinstance(result[key], dict)
            and isinstance(val, dict)
        ):
            result[key] = _merge(result[key], val)
        else:
            # If key is new or not both dicts, just overwrite/add
            result[key] = val
    return result


def load_config() -> Dict[str, Any]:
    """Load defaults and user overrides into memory, deeply merged.

    - Loads 'defaults.yaml' and (optionally) 'user.yaml' from the config folder.
    - Returns the deep-merged config dict.
    """
    global _defaults, _overrides
    repo_root = Path(__file__).resolve().parents[2]
    defaults_path = repo_root / "config" / "defaults.yaml"
    user_path = repo_root / "config" / "user.yaml"

    # Load defaults from YAML
    with open(defaults_path, encoding="utf-8") as f:
        _defaults = yaml.safe_load(f) or {}

    # Load overrides from YAML, if exists
    if user_path.exists():
        with open(user_path, encoding="utf-8") as f:
            _overrides = yaml.safe_load(f) or {}
    else:
        _overrides = {}

    # Return merged result, priority to overrides
    return _merge(_defaults, _overrides)


_settings = load_config()


def get_setting(
    key: str, default: Any | None = None, *, required: bool = False
) -> Any:
    """Return the configuration value for *key*, checking overrides before defaults.

    Dotted keys (e.g., 'db.host') supported for nested lookups.
    If not found, returns `default`. Raises if required and missing.
    """
    keys = key.split(".")
    value = _deep_get(_overrides, keys)
    if value is None:
        value = _deep_get(_defaults, keys)
    if value is None:
        value = default
    if required and (value is None or value == "REPLACE_ME"):
        raise RuntimeError(f"Missing required setting: {key}")
    return value


def get_constant(key: str, default: Any | None = None) -> Any:
    """Return a constant from the defaults file, without checking overrides."""
    keys = key.split(".")
    value = _deep_get(_defaults, keys)
    if value is None:
        value = default
    return value


__all__ = ["get_setting", "get_constant", "load_config"]
