"""Work context (sacho) — precedence, windows, action evidence, state safety."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from sillok.sacho import decide, match_explicit, path_profile, render_line, replay, resolve, vote
from sillok.sacho.state import FileLock, prune, session_file, session_hash

H = 3600.0
PROFILES = [
    {
        "id": "review",
        "label": "Code review",
        "action_signals": {"path_prefixes": ["src/", "tests/"]},
        "guide_refs": ["docs/sop/review.md"],
    },
    {
        "id": "report",
        "label": "Reporting",
        "action_signals": {"path_prefixes": ["docs/reports/"], "engagement_types": ["consulting"]},
        "priority": 5,
    },
    {
        "id": "docs",
        "label": "Docs",
        "action_signals": {"path_prefixes": ["docs/"]},
        "guide_refs": ["../outside.md", "docs/sop/docs.md"],
    },
]


def test_decide_explicit_then_inherit_within_gap() -> None:
    s1 = decide({}, "review", None, 1000.0)
    assert s1["source"] == "explicit" and s1["id"] == "review"
    s2 = decide(s1, None, None, 1000.0 + H)
    assert s2["source"] == "inherited" and s2["id"] == "review"


def test_decide_gap_and_anchor_expire() -> None:
    s1 = decide({}, "review", None, 0.0)
    assert decide(s1, None, None, 2 * H + 1)["id"] is None  # gap > 2 h
    chain = s1
    for t in (1.5 * H, 3.0 * H):
        chain = decide(chain, None, None, t)
        assert chain["id"] == "review"
    assert decide(chain, None, None, 4 * H + 1)["id"] is None  # anchor > 4 h despite short gaps


def test_decide_precedence_explicit_over_action() -> None:
    assert decide({}, "review", "report", 0.0)["id"] == "review"
    assert decide({}, None, "report", 0.0)["source"] == "action"


def test_path_profile_longest_prefix_then_engagement() -> None:
    assert path_profile("docs/reports/q3.md", PROFILES) == "report"
    assert path_profile("./docs/guide.md", PROFILES) == "docs"
    assert (
        path_profile("clients/acme/plan.md", PROFILES, [("clients/acme", ["consulting"])])
        == "report"
    )
    assert path_profile("misc/x.md", PROFILES) is None


def test_path_profile_keeps_leading_dot() -> None:
    profiles = [{"id": "cfg", "action_signals": {"path_prefixes": [".github/"]}}]
    assert path_profile(".github/workflows/ci.yml", profiles) == "cfg"


def test_vote_needs_two_writes_and_seventy_percent_of_all_writes() -> None:
    writes = [(10.0, "src/a.py"), (11.0, "src/b.py"), (12.0, "notes/x.md")]
    assert vote(writes, 0.0, 20.0, PROFILES) is None  # 2/3 = 67 % < 70 %
    assert vote(writes + [(13.0, "tests/t.py")], 0.0, 20.0, PROFILES) == "review"  # 3/4
    assert vote([(10.0, "src/a.py")], 0.0, 20.0, PROFILES) is None  # one write


def test_resolve_without_session_or_when_disabled_is_noop(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert resolve(tmp_path, "", PROFILES, explicit_id="review") is None
    monkeypatch.setenv("SILLOK_WORK_CONTEXT", "off")
    assert resolve(tmp_path, "s1", PROFILES, explicit_id="review") is None
    assert not list(tmp_path.glob("*.json"))


def test_resolve_inherits_and_isolates_sessions(tmp_path: Path) -> None:
    first = resolve(tmp_path, "s1", PROFILES, explicit_id="review", now=100.0)
    assert first and first["source"] == "explicit" and first["guide"] == "docs/sop/review.md"
    follow = resolve(tmp_path, "s1", PROFILES, now=200.0)
    assert follow and follow["source"] == "inherited" and follow["id"] == "review"
    assert resolve(tmp_path, "s2", PROFILES, now=200.0) is None


def test_state_never_stores_raw_session_id(tmp_path: Path) -> None:
    resolve(tmp_path, "secret-session-id", PROFILES, explicit_id="review", now=1.0)
    blob = "".join(p.read_text() for p in tmp_path.glob("*.json"))
    assert "secret-session-id" not in blob
    assert (
        session_file(tmp_path, "secret-session-id").name
        == session_hash("secret-session-id") + ".json"
    )


def test_action_signal_and_writes_before_explicit_turn_do_not_count(tmp_path: Path) -> None:
    writes = [(90.0, "src/a.py"), (95.0, "src/b.py")]
    ctx = resolve(tmp_path, "s1", PROFILES, writes=writes, now=100.0)
    assert ctx and ctx["source"] == "action" and ctx["id"] == "review"
    resolve(tmp_path, "s1", PROFILES, explicit_id="docs", now=200.0)
    # the same pre-explicit writes must not flip the explicitly named work back
    ctx = resolve(tmp_path, "s1", PROFILES, writes=writes, now=300.0)
    assert ctx and ctx["id"] == "docs" and ctx["source"] == "inherited"


def test_guide_filter_skips_ineligible_references(tmp_path: Path) -> None:
    ctx = resolve(tmp_path, "s1", PROFILES, explicit_id="docs", now=1.0)
    assert (
        ctx and ctx["guide"] == "docs/sop/docs.md"
    )  # '../outside.md' rejected by the default filter
    ctx = resolve(tmp_path, "s2", PROFILES, explicit_id="docs", now=1.0, guide_ok=lambda r: False)
    assert ctx and ctx["guide"] is None


def test_corrupt_state_reads_as_empty(tmp_path: Path) -> None:
    session_file(tmp_path, "s1").write_text("{not json", encoding="utf-8")
    assert resolve(tmp_path, "s1", PROFILES, now=1.0) is None


def test_stale_writer_does_not_overwrite_newer_state(tmp_path: Path) -> None:
    resolve(tmp_path, "s1", PROFILES, explicit_id="review", now=500.0)
    resolve(tmp_path, "s1", PROFILES, explicit_id="docs", now=400.0)  # finished late, older turn
    saved = json.loads(session_file(tmp_path, "s1").read_text())
    assert saved["id"] == "review" and saved["last_seen"] == 500.0


def test_lock_contention_returns_decision_without_saving(tmp_path: Path) -> None:
    holder = FileLock(tmp_path / f"{session_hash('s1')}.lock", wait_s=0.0)
    with holder:
        assert holder.held
        ctx = resolve(tmp_path, "s1", PROFILES, explicit_id="review", now=1.0)
    assert ctx and ctx["id"] == "review"
    assert not session_file(tmp_path, "s1").exists()


def test_render_line_only_for_non_explicit_turns() -> None:
    assert render_line({"id": "review", "label": "Code review", "source": "explicit"}) == ""
    line = render_line(
        {
            "id": "review",
            "label": "Code review",
            "source": "inherited",
            "guide": "docs/sop/review.md",
        }
    )
    assert line == "[work context] Code review (inherited) · guide: docs/sop/review.md"
    assert render_line(None) == ""


def test_prune_runs_at_most_daily_and_keeps_global_files(tmp_path: Path) -> None:
    import os

    for i in range(205):
        p = tmp_path / f"{i:016x}.json"
        p.write_text("{}")
        os.utime(p, (0, 0))
    (tmp_path / "_playbook.json").write_text("{}")
    os.utime(tmp_path / "_playbook.json", (0, 0))
    prune(tmp_path, now=30 * 86400)
    assert not list(tmp_path.glob("0*.json"))
    assert (tmp_path / "_playbook.json").exists()
    (tmp_path / f"{1:016x}.json").write_text("{}")
    os.utime(tmp_path / f"{1:016x}.json", (0, 0))
    prune(tmp_path, now=30 * 86400 + 60)  # stamp is fresh → no second sweep today
    assert (tmp_path / f"{1:016x}.json").exists()


def test_replay_measures_lift_from_inheritance() -> None:
    turns = [
        {"session": "a", "ts": 0.0, "explicit_id": "review"},
        {"session": "a", "ts": 600.0},
        {"session": "a", "ts": 1200.0},
        {"session": "b", "ts": 0.0},
    ]
    result = replay(turns, PROFILES)
    assert result["turns"] == 4 and result["explicit_share"] == 0.25
    assert result["attributed_share"] == 0.75
    assert result["by_source"] == {"explicit": 1, "inherited": 2}


def test_match_explicit_counts_trigger_hits_and_breaks_ties_by_priority() -> None:
    profiles = [
        {"id": "review", "triggers": ["review", "PR"]},
        {"id": "report", "triggers": ["report", "review"], "priority": 5},
    ]
    assert match_explicit("please review this PR", profiles) == "review"  # 2 hits beat 1
    assert match_explicit("review the draft", profiles) == "report"  # tie → priority
    assert (
        match_explicit("fix the script that prints", profiles) is None
    )  # PR is a whole token only
