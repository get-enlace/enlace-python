"""Reads an OpenAPI 3.x document from a file/URL path or accepts an
already-parsed dict directly."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

SpecSource = str | Path | dict[str, Any]


def load_spec(source: SpecSource) -> dict[str, Any]:
    """Loads an OpenAPI document from `source`.

    `source` is either an already-parsed dict (returned unchanged) or a
    filesystem path (str or Path) to a .json/.yaml/.yml file, read fresh
    every call — the caller (enlace()'s /api/spec route) is what makes this
    "fresh on every request"; this function itself just does the read+parse.
    """
    if isinstance(source, dict):
        return source

    path = Path(source)
    raw = path.read_text(encoding="utf-8")
    if path.suffix in (".yaml", ".yml"):
        return yaml.safe_load(raw)
    return json.loads(raw)
