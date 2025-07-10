"""
Config loader for STP.

Loads YAML defaults, optional user overrides, and environment variables
with deep-merge logic and caching via lru_cache.
Provides get_setting() and get_constant() for dot-path access.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

import yaml
from dotenv import load_dotenv

# Load environment variables from .env into os.environ (if .env exists)
load_dotenv()


def load_user_config() -> Dict[str, Any]:
    """Load critical overrides from environment (.env or system env)."""
    # Pull API keys and database creds directly from environment variables
    return {
        "api_key": os.getenv("API_KEY"),
        "db_user": os.getenv("DB_USER"),
        "db_pass": os.getenv("DB_PASS"),
    }


def _deep_get(mapping: Dict[str, Any], keys: list[str]) -> Any:
    """Walk a nested dict by a list of keys; return None if any key is missing."""
    current: Any = mapping
    for key in keys:
        if not isinstance(current, dict):
            # If current level isn't a dict, path is invalid
            return None
        current = current.get(key)
    return current


def _merge(base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively deep-merge two dicts: nested dicts merge, others overwrite."""
    # Create a shallow copy so we don't mutate the original base dict
    result = dict(base)
    for key, val in update.items():
        # If both base and update have dicts at this key, merge them recursively
        if key in result and isinstance(result[key], dict) and isinstance(val, dict):
            result[key] = _merge(result[key], val)
        else:
            # Otherwise, the update value replaces or adds to the result
            result[key] = val
    return result


@lru_cache(maxsize=1)
def _load_defaults() -> Dict[str, Any]:
    """Load defaults.yaml once and cache it for fast subsequent access."""
    # Locate the repo root relative to this file
    root = Path(__file__).resolve().parents[2]
    path = root / "config" / "defaults.yaml"
    with open(path, encoding="utf-8") as f:
        # Safe-load YAML; return empty dict if file is empty
        return yaml.safe_load(f) or {}


@lru_cache(maxsize=1)
def _load_overrides() -> Dict[str, Any]:
    """Load user.yaml overrides once and cache; return empty dict if absent."""
    root = Path(__file__).resolve().parents[2]
    path = root / "config" / "user.yaml"
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    # No overrides file means no override entries
    return {}


@lru_cache(maxsize=1)
def load_config() -> Dict[str, Any]:
    """Merge defaults and user overrides into one config dict (cached)."""
    defaults = _load_defaults()
    overrides = _load_overrides()
    # Combine with override taking precedence
    return _merge(defaults, overrides)


def get_setting(
    key: str,
    default: Any | None = None,
    required: bool = False,
    env_override: bool = True,
) -> Any:
    """
    Retrieve a config value using dot-path lookup with this precedence:
      1. Environment variable (if env_override=True)
      2. user.yaml overrides
      3. defaults.yaml
      4. provided default arg

    Raises if 'required' is True and resulting value is missing or placeholder.
    """
    # 1) Check environment variables first (e.g., 'DB_HOST' for 'db.host')
    if env_override:
        env_key = key.upper().replace('.', '_')
        if (val := os.getenv(env_key)) is not None:
            return val

    # 2) Load merged config and attempt lookup in overrides then defaults
    keys = key.split('.')
    value = _deep_get(_load_overrides(), keys)
    if value is None:
        value = _deep_get(_load_defaults(), keys)
    if value is None:
        # 3) Fall back to function default if still missing
        value = default

    # 4) If marked required but missing or placeholder, error out
    if required and (value is None or value == "REPLACE_ME"):
        raise RuntimeError(f"Missing required setting: {key}")
    return value


def get_constant(key: str, default: Any | None = None) -> Any:
    """Fetch a constant from defaults.yaml only, ignoring user overrides."""
    keys = key.split('.')
    value = _deep_get(_load_defaults(), keys)
    # If not found, use provided default
    return default if value is None else value


__all__ = ["load_user_config", "load_config", "get_setting", "get_constant"]
