from pathlib import Path

import pytest

from sre_node_sentinel.policy import load_policy


def test_load_policy_rejects_duplicate_ids(tmp_path: Path) -> None:
    policy = tmp_path / "policy.yml"
    policy.write_text(
        "checks:\n  - {id: one, type: file_mode, expected: '0600'}\n"
        "  - {id: one, type: file_mode, expected: '0644'}\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="duplicate"):
        load_policy(policy)


def test_load_policy_requires_check_mapping(tmp_path: Path) -> None:
    policy = tmp_path / "policy.yml"
    policy.write_text("checks:\n  - not-a-mapping\n", encoding="utf-8")
    with pytest.raises(ValueError, match="mapping"):
        load_policy(policy)
