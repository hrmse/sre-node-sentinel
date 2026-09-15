"""Command-line entrypoint for scheduled, read-only audits."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .engine import AuditEngine
from .policy import load_policy
from .render import to_json, to_prometheus


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Audit Linux node configuration against a YAML policy"
    )
    parser.add_argument("--policy", required=True, type=Path, help="YAML policy file")
    parser.add_argument(
        "--root", type=Path, default=Path("/"), help="filesystem root for offline audits"
    )
    parser.add_argument("--format", choices=("json", "prometheus"), default="json")
    parser.add_argument(
        "--output", type=Path, help="write atomically to this file instead of stdout"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        policy_name, checks = load_policy(args.policy)
        results = AuditEngine(args.root).run(checks)
        rendered = (
            to_json(results, policy_name)
            if args.format == "json"
            else to_prometheus(results, policy_name)
        )
        if args.output:
            temporary = args.output.with_suffix(args.output.suffix + ".tmp")
            temporary.write_text(rendered, encoding="utf-8")
            temporary.replace(args.output)
        else:
            sys.stdout.write(rendered)
    except (OSError, ValueError) as exc:
        print(f"sre-node-sentinel: {exc}", file=sys.stderr)
        return 2
    return 1 if any(result.status.value == "fail" for result in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
