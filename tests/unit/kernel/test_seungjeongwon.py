"""Context budget (seungjeongwon) — collapse repeats, never lose a pointer, fail open."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from sillok.sacho.state import session_file
from sillok.seungjeongwon import (
    DEDUP_WINDOW_S,
    ContextBudget,
    SessionSeen,
    dedup_list_block,
    dedup_sections,
    reset,
)
from sillok.seungjeongwon.budget import MAX_KEYS

CONTRACT = "\n".join(
    [
        "## Pack contracts",
        "[report-quality]",
        "- cite evidence grades",
        "- keep uncertainty near the claim",
        "[exec-communication]",
        "- conclusion first",
        "Body coordinates: packs/methodology/report-quality.md",
    ]
)
PATHS = {"report-quality": "packs/methodology/report-quality.md"}


def _turn(tmp_path: Path, now: float, block: str = CONTRACT) -> str:
    budget = ContextBudget(tmp_path, "s1", now=now)
    out = budget.sections(block, PATHS)
    budget.save()
    return out


def test_repeat_within_window_collapses_to_pointer_and_keeps_tail(tmp_path: Path) -> None:
    assert _turn(tmp_path, 100.0) == CONTRACT
    second = _turn(tmp_path, 200.0)
    assert "- cite evidence grades" not in second
    assert "report-quality → packs/methodology/report-quality.md" in second
    assert second.endswith("Body coordinates: packs/methodology/report-quality.md")
    assert second.startswith("## Pack contracts")


def test_window_expiry_and_changed_content_show_again(tmp_path: Path) -> None:
    _turn(tmp_path, 0.0)
    assert _turn(tmp_path, DEDUP_WINDOW_S + 1) == CONTRACT
    changed = CONTRACT.replace("conclusion first", "decision first")
    out = _turn(tmp_path, DEDUP_WINDOW_S + 2, changed)
    assert "- decision first" in out and "- cite evidence grades" not in out


def test_inactive_without_session_dir_or_when_off(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert not ContextBudget(tmp_path, "", now=1.0).active
    assert not ContextBudget(None, "s1", now=1.0).active
    monkeypatch.setenv("SILLOK_CONTEXT_BUDGET", "off")
    budget = ContextBudget(tmp_path, "s1", now=1.0)
    assert not budget.active and budget.sections(CONTRACT) == CONTRACT


def test_reset_and_session_isolation(tmp_path: Path) -> None:
    _turn(tmp_path, 0.0)
    other = ContextBudget(tmp_path, "s2", now=10.0)
    assert other.sections(CONTRACT, PATHS) == CONTRACT
    reset(tmp_path, "s1")
    assert _turn(tmp_path, 20.0) == CONTRACT


def test_list_block_collapses_seen_lines_and_keeps_header(tmp_path: Path) -> None:
    block = "## Lessons (notes/)\n- Prefer tables for comparisons → tables.md\n- Number every requested item → numbering.md"
    seen = SessionSeen(tmp_path, "s1", now=0.0)
    assert dedup_list_block(block, seen, "pb") == block
    seen.now = 60.0
    out = dedup_list_block(block, seen, "pb")
    assert out.splitlines()[0] == "## Lessons (notes/)"
    assert "tables.md · numbering.md" in out


def test_list_block_never_grows_past_the_original(tmp_path: Path) -> None:
    block = "- x → `" + "very-long-file-name-" * 4 + ".md`"
    seen = SessionSeen(tmp_path, "s1", now=0.0)
    dedup_list_block(block, seen, "pb")
    seen.now = 60.0
    assert dedup_list_block(block, seen, "pb") == block


def test_future_timestamps_do_not_collapse(tmp_path: Path) -> None:
    _turn(tmp_path, 10_000.0)
    assert _turn(tmp_path, 5_000.0) == CONTRACT  # clock went backwards


def test_corrupt_state_fails_open_and_bad_entries_are_dropped(tmp_path: Path) -> None:
    path = session_file(tmp_path, "s1", "budget")
    path.write_text("{oops", encoding="utf-8")
    assert _turn(tmp_path, 1.0) == CONTRACT
    data = json.loads(path.read_text())
    data["seen"]["section:bogus"] = ["not-a-time", 3]
    path.write_text(json.dumps(data))
    second = _turn(tmp_path, 2.0)
    assert "report-quality →" in second  # valid entries still de-duplicate


def test_unparsed_block_is_returned_unchanged(tmp_path: Path) -> None:
    seen = SessionSeen(tmp_path, "s1", now=0.0)
    assert dedup_sections("free text without sections", seen) == "free text without sections"


def test_max_keys_keeps_newest(tmp_path: Path) -> None:
    seen = SessionSeen(tmp_path, "s1", now=0.0)
    for i in range(MAX_KEYS + 10):
        seen.now = float(i)
        seen.fresh(f"k{i}", "x")
    seen.save()
    kept = json.loads(session_file(tmp_path, "s1", "budget").read_text())["seen"]
    assert len(kept) == MAX_KEYS and "k0" not in kept and f"k{MAX_KEYS + 9}" in kept


def test_errors_return_original_block(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    budget = ContextBudget(tmp_path, "s1", now=1.0)

    def boom(*a: object, **k: object) -> str:
        raise RuntimeError("boom")

    monkeypatch.setattr("sillok.seungjeongwon.budget.dedup_sections", boom)
    assert budget.sections(CONTRACT) == CONTRACT
