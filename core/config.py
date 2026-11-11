"""
Loads the YAML files that ship next to the code: limits (config.yaml) and the
server instructions with the trigger map (instructions.yaml).
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

CONFIG_DIR = Path(__file__).resolve().parent
CONFIG_FILE = "config.yaml"
INSTRUCTIONS_FILE = "instructions.yaml"


@lru_cache(maxsize=None)
def load_yaml(name: str) -> dict[str, Any]:
    """Read one YAML file from the folder of this module.

    Args:
        name: File name, e.g. "config.yaml".

    Returns:
        The decoded document.

    Raises:
        FileNotFoundError: If the file is missing.
    """
    return yaml.safe_load((CONFIG_DIR / name).read_text(encoding="utf-8"))


def setting(*keys: str) -> Any:
    """Look up a value in config.yaml by its key path.

    Args:
        *keys: Keys from the top level down, e.g. ("docs", "ttl_days").

    Returns:
        The configured value.

    Raises:
        KeyError: If the path does not exist.
    """
    value: Any = load_yaml(CONFIG_FILE)
    for key in keys:
        value = value[key]
    return value
