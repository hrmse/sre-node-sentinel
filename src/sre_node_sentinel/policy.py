"""Policy loading with strict schema checks and safe YAML parsing."""

from __future__ import annotations

from pathlib import Path

import yaml

from .models import Check


def load_policy(path: Path) -> tuple[str, list[Check]]:
    """Load a policy file; refuse non-mapping documents and duplicate IDs."""
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict) or not isinstance(document.get("checks"), list):
        raise ValueError("policy must be a mapping with a 'checks' list")
    checks = [Check.from_mapping(item) for item in document["checks"] if isinstance(item, dict)]
    if len(checks) != len(document["checks"]):
        raise ValueError("every check must be a mapping")
    ids = [check.identifier for check in checks]
    if len(ids) != len(set(ids)):
        raise ValueError("policy contains duplicate check ids")
    name = str(document.get("name", path.stem))
    return name, checks
