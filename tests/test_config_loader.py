"""
test for config_loader
"""
from stp.config_loader import _deep_get


def test_deep_get_path_found():
    "variables are list, keys"
    config = {"a": {"b": 42}}
    assert _deep_get(config, ["a", "b"]) == 42
