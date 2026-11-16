"""Playbook (gyeongyeon) — rank by outcome, count once per session, shadow before auto."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from sillok.gyeongyeon import Playbook, classify
from sillok.sacho.state import FileLock, session_file

ITEMS = [
    {
        "id": "tables",
        "work_type": "report",
        "title": "Compare options in a table",
        "path": "lessons/tables.md",
        "created": "2026-01-01",
    },
    {
        "id": "numbering",
        "work_type": "report",
        "title": "Answer every numbered item",
        "path": "lessons/numbering.md",
        "created": "2026-02-01",
    },
    {
        "id": "evidence",
        "work_type": "report",
        "title": "Put evidence next to the claim",
        "path": "lessons/evidence.md",
        "created": "2026-03-01",
        "how": "origin",
    },
    {"id": "commits", "work_type": "code", "title": "Small commits", "path": "lessons/commits.md"},
]


@pytest.fixture(autouse=True)
def _no_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SILLOK_PLAYBOOK_MODE", raising=False)


def _pb(tmp_path: Path, mode: str = "auto") -> Playbook:
    pb = Playbook(tmp_path, mode=mode)
    pb.add_items(ITEMS)
    return pb


def _counters(pb: Playbook) -> dict:
    return pb.load()["counters"].get("report", {})


def test_classify() -> None:
    assert classify("go") == "helpful"
    assert classify("진행") == "helpful"
    assert classify("[pm] done") == "helpful"
    assert classify("that's wrong, you missed item 3") == "harmful"
    assert classify("누락됐어요 다시 해 주세요") == "harmful"
    assert classify("now draft the appendix") is None
    assert classify("<command-name>/goal</command-name>") is None
    assert classify("A가 아니라 B로 정리해 줘") is None


def test_select_ranks_by_beta_mean_then_tier_then_recency(tmp_path: Path) -> None:
    pb = _pb(tmp_path)
    data = pb.load()
    assert pb.select(data, "report") == [
        "evidence",
        "numbering",
        "tables",
    ]  # equal means → origin tier, then newest
    data["counters"]["report"] = {"tables": {"h": 3, "x": 0}, "evidence": {"h": 0, "x": 2}}
    assert pb.select(data, "report")[0] == "tables" and pb.select(data, "report")[-1] == "evidence"


def test_auto_prints_bounded_block_and_learns_from_acceptance(tmp_path: Path) -> None:
    pb = _pb(tmp_path)
    block = pb.turn("s1", "write the Q3 report", "report", "Reporting", now=100.0)
    assert block.startswith("## Lessons for Reporting") and len(block.encode()) <= 900
    pb.turn("s1", "go", "report", "Reporting", now=200.0)
    assert {k: v["h"] for k, v in _counters(pb).items()} == {
        "evidence": 1,
        "numbering": 1,
        "tables": 1,
    }


def test_shadow_records_control_counters_only_and_prints_nothing(tmp_path: Path) -> None:
    pb = _pb(tmp_path, mode="shadow")
    assert pb.turn("s1", "write the report", "report", now=100.0) == ""
    pb.turn("s1", "that's wrong", "report", now=200.0)
    c = _counters(pb)["tables"]
    assert c["sx"] == 1 and c["x"] == 0 and c["h"] == 0


def test_env_overrides_mode(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SILLOK_PLAYBOOK_MODE", "off")
    pb = _pb(tmp_path, mode="auto")
    assert pb.mode == "off" and pb.turn("s1", "write the report", "report", now=1.0) == ""
    assert not session_file(tmp_path, "s1", "playbook").exists()


def test_same_session_counts_once_per_outcome(tmp_path: Path) -> None:
    pb = _pb(tmp_path)
    t = 100.0
    pb.turn("s1", "write the report", "report", now=t)
    for _ in range(4):
        t += 60
        pb.turn("s1", "go", "report", now=t)
    assert _counters(pb)["tables"]["h"] == 1
    pb.turn("s2", "write the report", "report", now=t + 60)
    pb.turn("s2", "go", "report", now=t + 120)
    assert _counters(pb)["tables"]["h"] == 2


def test_stale_pending_and_neutral_input_do_not_update(tmp_path: Path) -> None:
    pb = _pb(tmp_path)
    pb.turn("s1", "write the report", "report", now=0.0)
    pb.turn("s1", "go", "report", now=3 * 3600.0)  # outside the 2 h outcome window
    pb.turn("s1", "add a chart to section 2", "report", now=3 * 3600.0 + 60)
    assert all(c.get("h", 0) == 0 and c.get("x", 0) == 0 for c in _counters(pb).values())


def test_pending_from_the_same_instant_is_not_judged(tmp_path: Path) -> None:
    pb = _pb(tmp_path)
    pb.turn("s1", "write the report", "report", now=100.0)
    pb.turn("s1", "go", "report", now=100.0)
    assert _counters(pb) == {}


def test_machine_input_neither_judges_nor_consumes(tmp_path: Path) -> None:
    pb = _pb(tmp_path)
    pb.turn("s1", "write the report", "report", now=100.0)
    before = session_file(tmp_path, "s1", "playbook").read_text()
    assert pb.turn("s1", "<system-reminder>ok</system-reminder>", "report", now=150.0) == ""
    assert session_file(tmp_path, "s1", "playbook").read_text() == before
    pb.turn("s1", "go", "report", now=200.0)
    assert _counters(pb)["tables"]["h"] == 1


def test_exposure_is_only_what_fits_in_the_block(tmp_path: Path) -> None:
    pb = Playbook(tmp_path, mode="auto")
    pb.add_items(
        [
            {"id": f"i{n}", "work_type": "report", "title": "x" * 500, "path": f"l/{n}.md"}
            for n in range(3)
        ]
    )
    block = pb.turn("s1", "write", "report", now=1.0)
    exposed = json.loads(session_file(tmp_path, "s1", "playbook").read_text())["items"]
    assert len(exposed) == block.count("\n- ") == 1


def test_no_session_touches_nothing(tmp_path: Path) -> None:
    pb = _pb(tmp_path)
    assert pb.turn("", "write the report", "report", now=1.0) == ""
    assert not list(tmp_path.glob("*.playbook.json"))


def test_lock_contention_leaves_pending_exposure_alone(tmp_path: Path) -> None:
    pb = _pb(tmp_path)
    pb.turn("s1", "write the report", "report", now=100.0)
    before = session_file(tmp_path, "s1", "playbook").read_text()
    with FileLock(tmp_path / "_playbook.lock", wait_s=0.0) as other:
        assert other.held
        assert pb.turn("s1", "go", "report", now=200.0) == ""
    assert session_file(tmp_path, "s1", "playbook").read_text() == before
    assert _counters(pb) == {}


def test_add_items_keeps_counters(tmp_path: Path) -> None:
    pb = _pb(tmp_path)
    pb.turn("s1", "write", "report", now=1.0)
    pb.turn("s1", "go", "report", now=2.0)
    pb.add_items(ITEMS)
    assert _counters(pb)["tables"]["h"] == 1


def test_promote_candidates_need_three_helpful_sessions_and_no_harm(tmp_path: Path) -> None:
    pb = _pb(tmp_path)
    t = 0.0
    for sid in ("a", "b", "c"):
        pb.turn(sid, "write", "report", now=t)
        pb.turn(sid, "go", "report", now=t + 1)
        t += 10
    ids = {c["item"] for c in pb.promote_candidates()}
    assert ids == {"tables", "numbering", "evidence"}
    pb.turn("d", "write", "report", now=t)
    pb.turn("d", "wrong, that's not what I asked", "report", now=t + 1)
    assert pb.promote_candidates() == []
