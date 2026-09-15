"""Typed policy and result models used by the audit engine."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class Status(StrEnum):
    PASS = "pass"
    FAIL = "fail"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class Check:
    """A single declarative verification. Values deliberately remain scalar."""

    identifier: str
    kind: str
    expected: str
    path: str | None = None
    key: str | None = None
    option: str | None = None
    severity: str = "medium"

    @classmethod
    def from_mapping(cls, raw: dict[str, Any]) -> Check:
        required = {"id", "type", "expected"}
        absent = required - raw.keys()
        if absent:
            raise ValueError(f"check missing required field(s): {', '.join(sorted(absent))}")
        identifier = str(raw["id"])
        if not identifier.replace("-", "").replace("_", "").isalnum():
            raise ValueError(f"invalid check id: {identifier!r}")
        return cls(
            identifier=identifier,
            kind=str(raw["type"]),
            expected=str(raw["expected"]),
            path=str(raw["path"]) if raw.get("path") else None,
            key=str(raw["key"]) if raw.get("key") else None,
            option=str(raw["option"]) if raw.get("option") else None,
            severity=str(raw.get("severity", "medium")),
        )


@dataclass(frozen=True)
class Result:
    check: Check
    status: Status
    observed: str | None
    detail: str

    def as_dict(self) -> dict[str, str | None]:
        return {
            "id": self.check.identifier,
            "type": self.check.kind,
            "severity": self.check.severity,
            "status": self.status,
            "expected": self.check.expected,
            "observed": self.observed,
            "detail": self.detail,
        }
