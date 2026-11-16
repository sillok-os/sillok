"""Memory recall (chunchugwan) — index, gates, redaction, budget, exposure log."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from sillok.chunchugwan import (
    chunk_note,
    connect,
    eligible_episode,
    hook_block,
    query_terms,
    redact,
    refresh_episodes,
    refresh_memory,
    render_block,
    search,
)

NOTE = """---
name: release-checklist
description: Release checklist for PyPI alpha publishing
type: reference
---
# Release
Bump the version, tag, build the wheel.
## Verify
Install the wheel in a fresh venv and import it.
"""


@pytest.fixture()
def memdir(tmp_path: Path) -> Path:
    d = tmp_path / "memory"
    d.mkdir()
    (d / "release-checklist.md").write_text(NOTE, encoding="utf-8")
    (d / "MEMORY.md").write_text("- index line\n", encoding="utf-8")
    (d / "old.md").write_text(
        "---\nname: old\nstatus: superseded\n---\nrelease wheel publishing\n", encoding="utf-8"
    )
    return d


def test_chunk_note_splits_by_heading_path_and_skips_index(memdir: Path) -> None:
    chunks = chunk_note(memdir / "release-checklist.md")
    assert [c["heading"] for c in chunks] == [
        "",
        "Release",
        "Release › Verify",
    ]  # preamble chunk keeps the note findable by title
    assert chunks[2]["line_start"] > chunks[1]["line_start"]
    assert chunk_note(memdir / "MEMORY.md") == []
    assert chunk_note(memdir / "old.md") == []


def test_query_terms_strip_korean_particles_and_stopwords() -> None:
    assert query_terms("릴리스를 배포하는 방법을 정리해줘") == ["릴리스", "배포"]
    assert query_terms("please make the wheel for pypi") == ["wheel", "pypi"]


def test_refresh_is_incremental(tmp_path: Path, memdir: Path) -> None:
    conn = connect(tmp_path / "r.db")
    first = refresh_memory(conn, memdir)
    assert (
        first["changed"] == 3
    )  # every regular .md is tracked; MEMORY.md and superseded notes yield zero chunks
    assert refresh_memory(conn, memdir)["changed"] == 0
    (memdir / "release-checklist.md").unlink()
    assert refresh_memory(conn, memdir)["removed"] == 1


def test_search_requires_a_title_or_heading_match(tmp_path: Path, memdir: Path) -> None:
    conn = connect(tmp_path / "r.db")
    refresh_memory(conn, memdir)
    hit = search(conn, "how do I verify the wheel release for pypi publishing")
    assert [m["path"] for m in hit["memory"]] == ["release-checklist.md"]
    miss = search(conn, "fresh venv import bump")  # body-only coincidence
    assert miss["memory"] == []


def test_episodes_exclude_agent_traffic_and_current_session(tmp_path: Path) -> None:
    episodes = tmp_path / "episodes.jsonl"
    rows = [
        {
            "episode_id": "e1",
            "session": "s-old",
            "ts": "2026-10-01T00:00:00Z",
            "prompt": "draft the quarterly churn report for the board",
            "artifacts": ["docs/reports/churn.md"],
            "corrected": True,
        },
        {
            "episode_id": "e2",
            "session": "s-now",
            "ts": "2026-11-01T00:00:00Z",
            "prompt": "draft the quarterly churn report again for the board",
        },
        {
            "episode_id": "e3",
            "session": "s-x",
            "ts": "2026-11-01T00:00:00Z",
            "prompt": "draft the quarterly churn report board",
            "traffic": "agent",
        },
        {"episode_id": "e4", "session": "s-y", "ts": "2026-11-01T00:00:00Z", "prompt": "go"},
    ]
    episodes.write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")
    assert [eligible_episode(r) for r in rows] == [True, True, False, False]
    conn = connect(tmp_path / "r.db")
    assert refresh_episodes(conn, episodes)["episodes"] == 2
    assert refresh_episodes(conn, episodes)["skipped"] == "unchanged"
    found = search(conn, "quarterly churn report for the board", exclude_session="s-now")
    assert [e["cid"] for e in found["episodes"]] == ["e:e1"]
    block = render_block(found)
    assert "→ docs/reports/churn.md · was corrected" in block


def test_redaction_masks_secrets_and_contacts_but_not_dates() -> None:
    masked = redact("key sk-ant-abc123def456 mail a.b@example.com tel 010-1234-5678 on 2026-11-16")
    assert "sk-ant" not in masked and "example.com" not in masked and "1234-5678" not in masked
    assert "2026-11-16" in masked
    assert redact("build 20261116 v0.3.1") == "build 20261116 v0.3.1"


def test_render_block_is_bounded() -> None:
    result = {
        "memory": [{"path": f"n{i}.md", "heading": "h", "title": "t" * 200} for i in range(10)],
        "episodes": [],
    }
    block = render_block(result)
    assert len(block.encode()) <= 900 and block.count("\n- ") <= 5


def test_hook_skips_short_opt_out_and_disabled(
    tmp_path: Path, memdir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db = tmp_path / "r.db"
    assert hook_block("release wheel", db=db, memory_dir=memdir) == ""  # < 24 chars
    long_q = "how do I verify the wheel release for pypi publishing"
    assert hook_block(long_q + " [no-recall]", db=db, memory_dir=memdir) == ""
    assert hook_block("/" + long_q, db=db, memory_dir=memdir) == ""
    monkeypatch.setenv("SILLOK_MEMORY_RECALL", "off")
    assert hook_block(long_q, db=db, memory_dir=memdir) == ""


def test_hook_returns_pointer_block_and_logs_ids_only(tmp_path: Path, memdir: Path) -> None:
    log = tmp_path / "exposure.jsonl"
    block = hook_block(
        "how do I verify the wheel release for pypi publishing",
        db=tmp_path / "r.db",
        memory_dir=memdir,
        session_id="raw-session-id",
        exposure_log=log,
    )
    assert block.startswith("## Recall") and "release-checklist.md" in block
    assert "Install the wheel" not in block  # never the note body
    row = json.loads(log.read_text().splitlines()[0])
    assert row["memory"] == ["release-checklist.md"] and "raw-session-id" not in log.read_text()


def test_hook_survives_an_unwritable_db(tmp_path: Path, memdir: Path) -> None:
    blocker = tmp_path / "file"
    blocker.write_text("x")
    assert (
        hook_block(
            "how do I verify the wheel release for pypi publishing",
            db=blocker / "r.db",
            memory_dir=memdir,
        )
        == ""
    )


@pytest.mark.skipif(os.name == "nt", reason="FIFO is POSIX-only")
def test_refresh_ignores_non_regular_files(tmp_path: Path, memdir: Path) -> None:
    os.mkfifo(memdir / "pipe.md")
    conn = connect(tmp_path / "r.db")
    assert refresh_memory(conn, memdir)["files"] == 3  # the FIFO is not counted
