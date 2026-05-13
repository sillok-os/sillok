#!/usr/bin/env python3
"""Fail CI if STATUS.md pack count disagrees with packs/registry.yaml.

Acceptance gate from issue #6: "STATUS.md and registry.yaml pack count must agree".
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
REGISTRY = REPO_ROOT / "packs" / "registry.yaml"
STATUS = REPO_ROOT / "STATUS.md"

CLAIM_RE = re.compile(r"Current count:\s*\*\*(\d+)\s+packs\*\*")


def main() -> int:
    registry = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    packs = registry.get("packs") or []
    actual = len(packs)

    text = STATUS.read_text(encoding="utf-8")
    m = CLAIM_RE.search(text)
    if not m:
        print(
            "::error file=STATUS.md::could not parse pack count "
            "(expected 'Current count: **N packs**')"
        )
        return 2

    claimed = int(m.group(1))
    if claimed != actual:
        print(
            f"::error::pack count drift — STATUS.md claims {claimed}, "
            f"packs/registry.yaml has {actual}. "
            "Update STATUS.md or registry.yaml to restore agreement."
        )
        return 1

    print(f"OK: STATUS.md and registry.yaml agree on {actual} packs.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
