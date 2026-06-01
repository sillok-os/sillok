"""Unit tests for sillok.telemetry.gate — schema-enforced write-gate."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from sillok.telemetry import gate as tg

VALID_V2 = {
    "trace_id": "tr-test-1",
    "timestamp": datetime.now(UTC).isoformat(),
    "input": {"message": "hello"},
    "output": {
        "selected_pack_ids": ["alpha"],
        "selected_categories": ["domain"],
        "confidence_label": "high",
        "applied_prompt_packs_line": "applied prompt packs: alpha",
    },
    "metadata": {"router_version": "v2"},
    "scores": {"confidence_score": 0.9},
}

VALID_LEGACY = {
    "timestamp": "2026-06-01T00:00:00Z",
    "message": "hello",
    "selected_pack_ids": ["alpha"],
    "selected_categories": ["domain"],
    "confidence": "high",
    "applied_prompt_packs_line": "applied prompt packs: alpha",
}

# Missing the required input/output/metadata/scores envelopes.
INVALID_V2 = {"trace_id": "tr-bad", "timestamp": datetime.now(UTC).isoformat()}


def test_valid_v2_passes() -> None:
    ok, err = tg.validate_v2(VALID_V2)
    assert ok, err


def test_valid_legacy_passes() -> None:
    ok, err = tg.validate_legacy(VALID_LEGACY)
    assert ok, err


def test_invalid_v2_rejected() -> None:
    ok, err = tg.validate_v2(INVALID_V2)
    assert not ok
    assert err


def test_write_v2_appends(tmp_path: Path) -> None:
    dest = tmp_path / "telemetry.jsonl"
    assert tg.write_v2(VALID_V2, dest) is True
    assert dest.read_text(encoding="utf-8").count("\n") == 1


def test_write_invalid_rejected_no_append(tmp_path: Path) -> None:
    dest = tmp_path / "telemetry.jsonl"
    assert tg.write_v2(INVALID_V2, dest) is False
    assert not dest.exists()  # a rejected row never creates the file


def test_divergence_hook_runs_and_never_breaks(tmp_path: Path) -> None:
    seen: list[str] = []
    tg.divergence_hook = lambda record: seen.append(record["trace_id"])
    try:
        assert tg.write_v2(VALID_V2, tmp_path / "a.jsonl") is True
        assert seen == ["tr-test-1"]

        def _boom(_record: dict) -> None:
            raise RuntimeError("hook must not break the write")

        tg.divergence_hook = _boom
        assert tg.write_v2(VALID_V2, tmp_path / "b.jsonl") is True
    finally:
        tg.divergence_hook = None
