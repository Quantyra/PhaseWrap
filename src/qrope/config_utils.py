from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Config root must be a mapping: {path}")
    return data


def apply_set(config: dict[str, Any], dotted_key: str, raw_value: str) -> None:
    cursor: dict[str, Any] = config
    parts = dotted_key.split(".")
    for part in parts[:-1]:
        value = cursor.get(part)
        if value is None:
            value = {}
            cursor[part] = value
        if not isinstance(value, dict):
            raise ValueError(f"Cannot set nested key under non-mapping '{part}'")
        cursor = value
    cursor[parts[-1]] = _coerce(raw_value)


def _coerce(value: str) -> Any:
    lowered = value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        return value
