"""Shared YAML configuration loading with clear errors."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_yaml(path: Path) -> dict[str, Any]:
    """Load a YAML mapping and reject missing, malformed, or wrong-shaped data."""
    try:
        with path.open("r", encoding="utf-8") as stream:
            result = yaml.safe_load(stream)
    except OSError as exc:
        raise RuntimeError(f"Unable to read configuration file {path}: {exc}") from exc
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid YAML in configuration file {path}: {exc}") from exc
    if not isinstance(result, dict):
        raise ValueError(f"Configuration file must contain a YAML mapping: {path}")
    return result
