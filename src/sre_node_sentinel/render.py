"""Stable JSON and Prometheus renderers for automation-friendly output."""

from __future__ import annotations

import json
import re

from .models import Result, Status


def to_json(results: list[Result], policy_name: str) -> str:
    payload = {"policy": policy_name, "results": [result.as_dict() for result in results]}
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def _label(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def _metric_name(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_:]", "_", value)


def to_prometheus(results: list[Result], policy_name: str) -> str:
    """Render one exactly-one status series per check, plus a failure summary."""
    lines = [
        "# HELP sre_node_sentinel_check_status Linux configuration check status (one-hot).",
        "# TYPE sre_node_sentinel_check_status gauge",
    ]
    for result in results:
        labels = f'policy="{_label(policy_name)}",check="{_label(result.check.identifier)}"'
        for status in Status:
            value = 1 if result.status == status else 0
            lines.append(f'sre_node_sentinel_check_status{{{labels},status="{status}"}} {value}')
    failed = sum(result.status == Status.FAIL for result in results)
    unknown = sum(result.status == Status.UNKNOWN for result in results)
    lines.extend(
        [
            "# HELP sre_node_sentinel_failed_checks Number of failed policy checks.",
            "# TYPE sre_node_sentinel_failed_checks gauge",
            f'sre_node_sentinel_failed_checks{{policy="{_label(policy_name)}"}} {failed}',
            "# HELP sre_node_sentinel_unknown_checks Number of indeterminate policy checks.",
            "# TYPE sre_node_sentinel_unknown_checks gauge",
            f'sre_node_sentinel_unknown_checks{{policy="{_label(policy_name)}"}} {unknown}',
        ]
    )
    return "\n".join(lines) + "\n"
