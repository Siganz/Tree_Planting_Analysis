"""Load configuration defaults and user overrides."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml

_defaults: Dict[str, Any] = {}
_overrides: Dict[str, Any] = {}


def _deep_get(mapping: Dict[str, Any], keys: list[str]) -> Any:
    val: Any = mapping
    for key in keys:
        if isinstance(val, dict):
            val = val.get(key)
        else:
            return None
    return val


def _merge(base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
    result = dict(base)
    for key, val in update.items():
        if (
            key in result
            and isinstance(result[key], dict)
            and isinstance(val, dict)
        ):
            result[key] = _merge(result[key], val)
        else:
            result[key] = val
    return result


def load_config() -> Dict[str, Any]:
    """Load defaults and user overrides into memory."""
    global _defaults, _overrides
    repo_root = Path(__file__).resolve().parents[2]
    defaults_path = repo_root / "config" / "defaults.yaml"
    user_path = repo_root / "config" / "user.yaml"

    with open(defaults_path, encoding="utf-8") as f:
        _defaults = yaml.safe_load(f) or {}

    if user_path.exists():
        with open(user_path, encoding="utf-8") as f:
            _overrides = yaml.safe_load(f) or {}
    else:
        _overrides = {}

    return _merge(_defaults, _overrides)


_settings = load_config()


def get_setting(
    key: str, default: Any | None = None, *, required: bool = False
) -> Any:
    """Return the configuration value for *key* with priority to overrides."""
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
    """Return a constant from the defaults file."""
    keys = key.split(".")
    value = _deep_get(_defaults, keys)
    if value is None:
        value = default
    return value


__all__ = ["get_setting", "get_constant", "load_config"]
