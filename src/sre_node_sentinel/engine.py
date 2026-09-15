"""Read-only Linux configuration checks.

The engine never invokes a shell or changes a target. `root` makes every check
testable against a filesystem fixture and supports offline image inspection.
"""

from __future__ import annotations

import configparser
from collections.abc import Callable
from pathlib import Path

from .models import Check, Result, Status


class AuditEngine:
    def __init__(self, root: Path = Path("/")) -> None:
        self.root = root.resolve()

    def _path(self, absolute: str) -> Path:
        candidate = (self.root / absolute.lstrip("/")).resolve()
        if self.root not in (candidate, *candidate.parents):
            raise ValueError(f"path escapes audit root: {absolute}")
        return candidate

    def run(self, checks: list[Check]) -> list[Result]:
        dispatch: dict[str, Callable[[Check], Result]] = {
            "file_mode": self._file_mode,
            "sshd_directive": self._sshd_directive,
            "sysctl": self._sysctl,
            "mount_option": self._mount_option,
            "systemd_setting": self._systemd_setting,
        }
        results: list[Result] = []
        for check in checks:
            handler = dispatch.get(check.kind)
            if handler is None:
                results.append(Result(check, Status.UNKNOWN, None, "unsupported check type"))
                continue
            try:
                results.append(handler(check))
            except (OSError, ValueError, configparser.Error) as exc:
                results.append(Result(check, Status.UNKNOWN, None, f"cannot evaluate: {exc}"))
        return results

    @staticmethod
    def _result(check: Check, observed: str | None, detail: str) -> Result:
        status = Status.PASS if observed == check.expected else Status.FAIL
        return Result(check, status, observed, detail)

    def _file_mode(self, check: Check) -> Result:
        if not check.path:
            raise ValueError("file_mode needs path")
        target = self._path(check.path)
        mode = format(target.stat().st_mode & 0o7777, "04o")
        return self._result(check, mode, str(target))

    def _sshd_directive(self, check: Check) -> Result:
        if not check.key:
            raise ValueError("sshd_directive needs key")
        config_path = self._path(check.path or "/etc/ssh/sshd_config")
        if not config_path.exists():
            raise ValueError(f"missing {config_path}")
        # sshd uses the first global setting encountered. Match directives
        # case-insensitively and intentionally do not guess Match-block scope.
        for line in config_path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.split("#", 1)[0].strip()
            if not line or line.lower().startswith("match "):
                continue
            parts = line.split(None, 1)
            if len(parts) == 2 and parts[0].lower() == check.key.lower():
                return self._result(check, parts[1].strip().lower(), str(config_path))
        return Result(check, Status.UNKNOWN, None, f"directive not set in {config_path}")

    def _sysctl(self, check: Check) -> Result:
        if not check.key:
            raise ValueError("sysctl needs key")
        proc_value = self._path("/proc/sys/" + check.key.replace(".", "/"))
        if proc_value.exists():
            observed = proc_value.read_text(encoding="utf-8").strip()
            return self._result(check, observed, str(proc_value))
        # Offline image mode: use the last setting in lexical configuration order.
        settings: dict[str, str] = {}
        directories = (
            "/usr/lib/sysctl.d",
            "/usr/local/lib/sysctl.d",
            "/run/sysctl.d",
            "/etc/sysctl.d",
        )
        for directory in directories:
            candidate = self._path(directory)
            if candidate.exists():
                for item in sorted(candidate.glob("*.conf")):
                    settings.update(self._parse_assignments(item))
        sysctl_conf = self._path("/etc/sysctl.conf")
        if sysctl_conf.exists():
            settings.update(self._parse_assignments(sysctl_conf))
        observed = settings.get(check.key)
        if observed is None:
            return Result(check, Status.UNKNOWN, None, "sysctl is not configured")
        return self._result(check, observed, "sysctl configuration")

    @staticmethod
    def _parse_assignments(path: Path) -> dict[str, str]:
        values: dict[str, str] = {}
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.split("#", 1)[0].strip()
            if "=" in line:
                key, value = (part.strip() for part in line.split("=", 1))
                if key:
                    values[key] = value
        return values

    def _mount_option(self, check: Check) -> Result:
        if not check.path or not check.option:
            raise ValueError("mount_option needs path and option")
        mountinfo = self._path("/proc/self/mountinfo")
        if not mountinfo.exists():
            return Result(check, Status.UNKNOWN, None, "mountinfo unavailable (offline audit)")
        for line in mountinfo.read_text(encoding="utf-8").splitlines():
            fields = line.split()
            if len(fields) > 5 and fields[4] == check.path:
                options = set(fields[5].split(","))
                observed = "present" if check.option in options else "absent"
                return self._result(check, observed, f"mount options: {fields[5]}")
        return Result(check, Status.UNKNOWN, None, f"mount point not found: {check.path}")

    def _systemd_setting(self, check: Check) -> Result:
        if not check.path or not check.key:
            raise ValueError("systemd_setting needs path and key")
        unit = self._path(check.path)
        parser = configparser.ConfigParser(interpolation=None, strict=False)
        parser.optionxform = str
        parser.read(unit, encoding="utf-8")
        section, _, key = check.key.partition(".")
        if not section or not key or not parser.has_option(section, key):
            return Result(check, Status.UNKNOWN, None, f"setting not found: {check.key}")
        return self._result(check, parser.get(section, key), str(unit))
