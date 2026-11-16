"""Router golden set (tests/goldens/router-golden.jsonl) as a CI gate.

Until 0.3.1 the golden file existed but nothing ran it, and Tier 1 returned
every pack with a non-zero precedence (5.00 candidates per message on
average). Positive rows guard recall; ``negative`` rows guard the
no-match path; the candidate budget guards against precedence-only noise.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from sillok.naru.router_2tier import load_registry, tier1_match

ROOT = Path(__file__).resolve().parents[2]
GOLDEN = ROOT / "tests" / "goldens" / "router-golden.jsonl"
ROWS = [
    json.loads(line) for line in GOLDEN.read_text(encoding="utf-8").splitlines() if line.strip()
]
PACKS = load_registry(ROOT / "packs" / "registry.yaml")

POSITIVE = [r for r in ROWS if r["expected_pack_ids"]]
NEGATIVE = [r for r in ROWS if not r["expected_pack_ids"]]


def _ids(message: str) -> list[str]:
    return [c["pack_id"] for c in tier1_match(message, PACKS, top_k=5)]


def test_golden_has_both_kinds() -> None:
    assert len(POSITIVE) >= 30
    assert len(NEGATIVE) >= 4


def test_top1_accuracy_at_least_90_percent() -> None:
    misses = [
        (r["id"], _ids(r["message"]))
        for r in POSITIVE
        if (_ids(r["message"]) or [None])[0] not in r["expected_pack_ids"]
    ]
    assert len(misses) <= len(POSITIVE) // 10, f"top-1 misses: {misses}"


def test_expected_pack_within_top5_for_every_positive_row() -> None:
    misses = [
        r["id"] for r in POSITIVE if not set(r["expected_pack_ids"]) & set(_ids(r["message"]))
    ]
    assert not misses, f"expected pack absent from top-5: {misses}"


@pytest.mark.parametrize("row", NEGATIVE, ids=[r["id"] for r in NEGATIVE])
def test_negative_rows_load_no_pack(row: dict) -> None:
    assert _ids(row["message"]) == []


def test_candidate_budget() -> None:
    average = sum(len(_ids(r["message"])) for r in ROWS) / len(ROWS)
    assert average <= 2.0, f"average candidates {average:.2f} — precedence noise is back"
