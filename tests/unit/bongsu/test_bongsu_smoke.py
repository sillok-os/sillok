"""Smoke tests for sillok.bongsu — telemetry post-update."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from sillok.bongsu import load_hits, patch_telemetry


@pytest.fixture
def telemetry_path(tmp_path: Path) -> Path:
    p = tmp_path / "telemetry.jsonl"
    p.write_text(
        json.dumps(
            {
                "message_hash": "abc123",
                "selected_pack_ids": ["alpha"],
                "knowledge_hit_count": None,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    return p


@pytest.fixture
def hits_path(tmp_path: Path) -> Path:
    p = tmp_path / "hits.json"
    p.write_text(
        json.dumps(
            {
                "hits": [
                    {"path": "vault/a.md", "tier": "A", "score": 0.91},
                    {"path": "vault/b.md", "tier": "B", "score": 0.7},
                ]
            }
        ),
        encoding="utf-8",
    )
    return p


def test_load_hits_summary_shape(hits_path: Path) -> None:
    summary = load_hits(hits_path)
    assert summary["knowledge_hit_count"] == 2
    assert summary["knowledge_hit_paths"] == ["vault/a.md", "vault/b.md"]
    assert summary["knowledge_hit_tiers"] == ["A", "B"]


def test_patch_telemetry_writes_back(
    telemetry_path: Path,
    hits_path: Path,
) -> None:
    summary = load_hits(hits_path)
    patched, row = patch_telemetry(
        telemetry_path,
        message_hash="abc123",
        hits=summary,
        pattern_freq=0,
    )
    assert patched is True
    assert row["knowledge_hit_count"] == 2
    assert row["knowledge_gap_label"] is None
    assert row["promotion_candidate"] is False
    persisted = json.loads(telemetry_path.read_text().splitlines()[0])
    assert persisted["knowledge_hit_count"] == 2


def test_patch_telemetry_promotion_candidate_on_zero_hits(
    telemetry_path: Path,
    tmp_path: Path,
) -> None:
    empty_hits = tmp_path / "empty.json"
    empty_hits.write_text(json.dumps({"hits": []}), encoding="utf-8")
    summary = load_hits(empty_hits)
    patched, row = patch_telemetry(
        telemetry_path,
        message_hash="abc123",
        hits=summary,
        pattern_freq=5,
    )
    assert patched is True
    assert row["knowledge_gap_label"] == "no-hits"
    assert row["promotion_candidate"] is True


def test_patch_telemetry_returns_false_when_hash_missing(
    telemetry_path: Path,
    hits_path: Path,
) -> None:
    summary = load_hits(hits_path)
    patched, row = patch_telemetry(
        telemetry_path,
        message_hash="not-in-file",
        hits=summary,
    )
    assert patched is False
    assert row == {}


def test_patch_telemetry_dry_run_does_not_rewrite(
    telemetry_path: Path,
    hits_path: Path,
) -> None:
    original = telemetry_path.read_text()
    summary = load_hits(hits_path)
    patched, _ = patch_telemetry(
        telemetry_path,
        message_hash="abc123",
        hits=summary,
        dry_run=True,
    )
    assert patched is True
    assert telemetry_path.read_text() == original
