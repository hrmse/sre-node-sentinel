import os
from pathlib import Path

from sre_node_sentinel.engine import AuditEngine
from sre_node_sentinel.models import Check, Status


def write(root: Path, name: str, content: str, mode: int | None = None) -> Path:
    target = root / name.lstrip("/")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    if mode is not None:
        os.chmod(target, mode)
    return target


def test_engine_evaluates_supported_checks(tmp_path: Path) -> None:
    write(tmp_path, "/etc/ssh/sshd_config", "PermitRootLogin no\n", 0o600)
    write(tmp_path, "/proc/sys/net/ipv4/conf/all/rp_filter", "1\n")
    write(tmp_path, "/proc/self/mountinfo", "42 1 0:42 / /tmp rw,noexec,nosuid - tmpfs tmpfs rw\n")
    write(
        tmp_path,
        "/etc/systemd/system/sre-node-sentinel.service",
        "[Service]\nNoNewPrivileges=true\n",
    )
    checks = [
        Check("ssh", "sshd_directive", "no", key="PermitRootLogin"),
        Check("mode", "file_mode", "0600", path="/etc/ssh/sshd_config"),
        Check("sysctl", "sysctl", "1", key="net.ipv4.conf.all.rp_filter"),
        Check("mount", "mount_option", "present", path="/tmp", option="noexec"),
        Check(
            "unit",
            "systemd_setting",
            "true",
            path="/etc/systemd/system/sre-node-sentinel.service",
            key="Service.NoNewPrivileges",
        ),
    ]
    results = AuditEngine(tmp_path).run(checks)
    assert [result.status for result in results] == [Status.PASS] * 5


def test_unknown_type_and_absent_sshd_directive_are_indeterminate(tmp_path: Path) -> None:
    write(tmp_path, "/etc/ssh/sshd_config", "PasswordAuthentication yes\n")
    results = AuditEngine(tmp_path).run(
        [
            Check("unknown", "shell_command", "yes"),
            Check("unset", "sshd_directive", "no", key="PermitRootLogin"),
        ]
    )
    assert [item.status for item in results] == [Status.UNKNOWN, Status.UNKNOWN]
