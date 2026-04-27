"""Smoke tests for sillok.bongsu.search — vault corpus search."""
from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest

from sillok.bongsu import (
    build_index,
    canonicalize_scope,
    extract_body_preview,
    filter_notes,
    note_matches_scope,
    parse_frontmatter,
    print_stats,
)


@pytest.fixture
def vault(tmp_path: Path) -> Path:
    v = tmp_path / "vault"
    v.mkdir()
    (v / "alpha.md").write_text(
        dedent(
            """
            ---
            title: Pricing pattern
            type: pattern
            scope: acme
            retrieval_tier: A
            tags: [pricing, b2b]
            ---

            Body of the pricing pattern note.
            """
        ).strip(),
        encoding="utf-8",
    )
    (v / "subdir").mkdir()
    (v / "subdir" / "beta.md").write_text(
        dedent(
            """
            ---
            title: Risk register decision
            type: decision
            scope: globex
            retrieval_tier: B
            ---

            Decision content.
            """
        ).strip(),
        encoding="utf-8",
    )
    (v / "no-fm.md").write_text("just a body, no frontmatter\n", encoding="utf-8")
    (v / ".obsidian").mkdir()
    (v / ".obsidian" / "config.md").write_text("# secret", encoding="utf-8")
    return v


def test_parse_frontmatter_extracts_known_keys() -> None:
    content = dedent(
        """
        ---
        title: Hello
        type: pattern
        tags: [a, b]
        ---

        body
        """
    ).strip()
    fm = parse_frontmatter(content)
    assert fm["title"] == "Hello"
    assert fm["type"] == "pattern"
    assert fm["tags"] == ["a", "b"]


def test_parse_frontmatter_returns_empty_when_absent() -> None:
    assert parse_frontmatter("no frontmatter here") == {}


def test_extract_body_preview_truncates() -> None:
    full = "---\ntitle: t\n---\n\n" + "\n".join(f"line {i}" for i in range(20))
    preview = extract_body_preview(full, max_lines=5)
    assert preview.count("\n") == 4


def test_build_index_indexes_md_with_frontmatter(vault: Path) -> None:
    notes = build_index(vault)
    paths = {n["_path"] for n in notes}
    assert "alpha.md" in paths
    assert "subdir/beta.md" in paths
    assert "no-fm.md" in paths  # included even without frontmatter
    assert ".obsidian/config.md" not in {p for p in paths}


def test_filter_notes_by_scope(vault: Path) -> None:
    notes = build_index(vault)
    acme_only = filter_notes(notes, scope="acme")
    assert len(acme_only) == 1
    assert acme_only[0]["title"] == "Pricing pattern"


def test_filter_notes_by_type(vault: Path) -> None:
    notes = build_index(vault)
    decisions = filter_notes(notes, note_type="decision")
    assert len(decisions) == 1
    assert decisions[0]["type"] == "decision"


def test_filter_notes_by_tier(vault: Path) -> None:
    notes = build_index(vault)
    tier_a = filter_notes(notes, tier="A")
    assert len(tier_a) == 1
    assert tier_a[0]["retrieval_tier"] == "A"


def test_canonicalize_scope_with_alias_map() -> None:
    aliases = {"acme-corp": "acme", "acme-inc": "acme"}
    assert canonicalize_scope("acme-corp", aliases) == "acme"
    assert canonicalize_scope("globex", aliases) == "globex"
    assert canonicalize_scope("", aliases) == ""


def test_note_matches_scope_with_alias_resolution() -> None:
    note = {"scope": "acme-inc"}
    aliases = {"acme-inc": "acme"}
    assert note_matches_scope(note, "acme", aliases) is True
    assert note_matches_scope(note, "globex", aliases) is False


def test_note_matches_scope_with_list_value() -> None:
    note = {"scope": ["acme", "globex"]}
    assert note_matches_scope(note, "acme", {}) is True
    assert note_matches_scope(note, "globex", {}) is True


def test_print_stats_emits_counts(vault: Path) -> None:
    notes = build_index(vault)
    output = print_stats(notes)
    assert "Total indexed notes:" in output
    assert "Top 15 Scopes" in output


def test_excluded_directories_are_skipped(vault: Path) -> None:
    notes = build_index(vault)
    paths = {n["_path"] for n in notes}
    for p in paths:
        assert ".obsidian" not in p
