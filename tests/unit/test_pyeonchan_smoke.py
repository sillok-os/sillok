"""Smoke tests for sillok.pyeonchan (Phase 0 md-only)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from sillok.pyeonchan import Atom, ingest_md, watch_md


def _make_vault(tmp_path: Path) -> Path:
    vault = tmp_path / "vault"
    vault.mkdir()
    (vault / "note-1.md").write_text(
        "---\ntitle: Hello\n---\n\nbody one\n",
        encoding="utf-8",
    )
    (vault / "subdir").mkdir()
    (vault / "subdir" / "note-2.md").write_text(
        "no frontmatter here\n",
        encoding="utf-8",
    )
    (vault / "ignore.txt").write_text("not markdown", encoding="utf-8")
    (vault / ".obsidian").mkdir()
    (vault / ".obsidian" / "config.md").write_text("# secret", encoding="utf-8")
    return vault


def test_ingest_indexes_md_files(tmp_path: Path) -> None:
    vault = _make_vault(tmp_path)

    n = ingest_md(vault)
    assert n == 2  # ignore.txt and .obsidian/* skipped

    index_path = vault / ".sillok-janggyeong" / "index.jsonl"
    assert index_path.exists()
    rows = [json.loads(line) for line in index_path.read_text().splitlines() if line]
    assert len(rows) == 2
    titles = {r.get("frontmatter", {}).get("title") for r in rows}
    assert "Hello" in titles


def test_atom_roundtrip(tmp_path: Path) -> None:
    a = Atom(path="x.md", sha256="deadbeef", mtime=0.0, size=10)
    d = a.to_dict()
    assert d["path"] == "x.md"
    assert d["sha256"] == "deadbeef"
    assert d["frontmatter"] == {}


def test_watch_runs_one_cycle(tmp_path: Path) -> None:
    vault = _make_vault(tmp_path)
    watch_md(vault, interval=0.0, once=True)
    assert (vault / ".sillok-janggyeong" / "index.jsonl").exists()


@pytest.mark.parametrize("badname", ["..", "/etc/passwd"])
def test_ingest_rejects_nonexistent_vault(tmp_path: Path, badname: str) -> None:
    target = tmp_path / "does-not-exist"
    with pytest.raises(NotADirectoryError):
        ingest_md(target)
