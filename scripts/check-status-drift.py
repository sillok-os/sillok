#!/usr/bin/env python3
"""Fail CI if STATUS.md or README.md pack count disagrees with packs/registry.yaml.

Acceptance gate from issue #6: "STATUS.md and registry.yaml pack count must agree".
Extended (Wave 1b retro action P1): README banner pack count must also agree.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
REGISTRY = REPO_ROOT / "packs" / "registry.yaml"
STATUS = REPO_ROOT / "STATUS.md"
README = REPO_ROOT / "README.md"

STATUS_CLAIM_RE = re.compile(r"Current count:\s*\*\*(\d+)\s+packs\*\*")
README_BANNER_RE = re.compile(
    r"\*\*Status\*\*:\s*`v[0-9a-z.]+`\s*alpha\s*[—-]\s*(\d+)\s+packs"
)


def check_file(path: Path, regex: re.Pattern[str], actual: int, label: str) -> int:
    text = path.read_text(encoding="utf-8")
    m = regex.search(text)
    if not m:
        print(
            f"::error file={path.name}::could not parse pack count from {label} "
            f"(expected pattern {regex.pattern!r})"
        )
        return 2
    claimed = int(m.group(1))
    if claimed != actual:
        print(
            f"::error file={path.name}::pack count drift — {label} claims {claimed}, "
            f"packs/registry.yaml has {actual}. "
            f"Update {path.name} or registry.yaml to restore agreement."
        )
        return 1
    print(f"OK: {label} agrees with registry.yaml on {actual} packs.")
    return 0


def main() -> int:
    registry = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    packs = registry.get("packs") or []
    actual = len(packs)

    rc1 = check_file(STATUS, STATUS_CLAIM_RE, actual, "STATUS.md `Current count`")
    rc2 = check_file(README, README_BANNER_RE, actual, "README.md Status banner")

    return max(rc1, rc2)


if __name__ == "__main__":
    sys.exit(main())
