"""Smoke tests for sillok.yeonryun.disposition."""
from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest

from sillok.yeonryun import (
    CROSS_REPO_THRESHOLD,
    LOCAL_THRESHOLD,
    determine_disposition,
    extract_body,
    generate_atomic_note,
    identify_extractable_atoms,
    parse_frontmatter,
    process_file,
    scan_directory,
    score_reusability,
)


# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------


@pytest.fixture
def reusable_doc() -> str:
    body = dedent(
        """
        # Pricing Pattern Playbook

        ## Pattern: Tiered Pricing
        A reusable workflow for SaaS pricing.

        | tier | seats | price |
        |------|-------|-------|
        | starter | 1-5 | $9 |
        | pro | 6-50 | $29 |
        | enterprise | 51+ | custom |

        ```python
        def price(seats):
            ...
        ```

        ```python
        def upgrade(plan):
            ...
        ```

        ## Decision Rule
        Trigger upgrade when seat utilization exceeds 80%.

        ## Checklist
        - validate price card
        - validate seat counter
        - validate upgrade prompt

        ## Best Practice
        Always use a price metric tied to value delivered.

        ## Lesson
        We learned that flat seat pricing leaks revenue at scale.
        """
    ).strip()
    return body + "\n" + ("filler line\n" * 60)


@pytest.fixture
def ephemeral_doc() -> str:
    return dedent(
        """
        # Hotfix log

        Quick debug session for a one-time issue. The workaround was to
        bypass the cache for the affected request only.
        """
    ).strip() + "\n" + ("noise\n" * 5)


# ----------------------------------------------------------------------
# Tests — pure helpers
# ----------------------------------------------------------------------


def test_parse_frontmatter_extracts_keys() -> None:
    content = "---\ntitle: Hello\ntype: pattern\n---\n\nbody"
    fm = parse_frontmatter(content)
    assert fm["title"] == "Hello"
    assert fm["type"] == "pattern"


def test_extract_body_strips_frontmatter() -> None:
    content = "---\nfoo: bar\n---\n\nthis is the body."
    assert extract_body(content) == "this is the body."


def test_score_reusability_rewards_signals(reusable_doc: str) -> None:
    score, signals = score_reusability(reusable_doc)
    assert score >= CROSS_REPO_THRESHOLD
    types = {s["type"] for s in signals}
    assert "pattern" in types
    assert "decision" in types
    assert "checklist" in types


def test_score_reusability_penalizes_ephemeral(ephemeral_doc: str) -> None:
    score, signals = score_reusability(ephemeral_doc)
    assert score < LOCAL_THRESHOLD
    assert any(s["type"] == "ephemeral" for s in signals)


# ----------------------------------------------------------------------
# Tests — disposition
# ----------------------------------------------------------------------


def test_determine_disposition_too_short_returns_none() -> None:
    result = determine_disposition("short", {})
    assert result["disposition"] == "none"
    assert "too short" in result["reason"]


def test_determine_disposition_high_score_is_cross_repo(reusable_doc: str) -> None:
    result = determine_disposition(reusable_doc, {})
    assert result["disposition"] == "cross-repo-reusable"
    assert result["score"] >= CROSS_REPO_THRESHOLD
    assert result["extractable_atoms"]


def test_determine_disposition_carries_source_tier() -> None:
    body = "# heading\n\n" + ("filler text " * 100)
    result = determine_disposition(body, {"retrieval_tier": "A", "quality_score": "0.9"})
    assert result.get("source_retrieval_tier") == "A"
    assert result.get("source_quality_score") == "0.9"


def test_identify_extractable_atoms_dedupes_and_caps() -> None:
    body = "pattern pattern pattern checklist checklist decision template case prompt insight"
    _, signals = score_reusability(body)
    atoms = identify_extractable_atoms(body, signals, {})
    types = [a["knowledge_type"] for a in atoms]
    assert len(types) == len(set(types))
    assert len(atoms) <= 5


def test_identify_extractable_atoms_honors_cross_repo_optout() -> None:
    body = "pattern checklist decision template"
    _, signals = score_reusability(body)
    assert identify_extractable_atoms(body, signals, {"cross_repo": "false"}) == []
    assert identify_extractable_atoms(body, signals, {"disposition": "none"}) == []


# ----------------------------------------------------------------------
# Tests — atomic note generation
# ----------------------------------------------------------------------


def test_generate_atomic_note_uses_source_repo_override() -> None:
    atom = {"knowledge_type": "pattern", "source_section": "Pattern", "reusability": "high"}
    note = generate_atomic_note(
        atom, "research/foo.md", {}, "## Pattern\nbody",
        source_repo="acme/widget",
    )
    assert "source_repo: acme/widget" in note
    assert "source-system: sillok.yeonryun" in note


def test_generate_atomic_note_falls_back_to_source_topic() -> None:
    atom = {"knowledge_type": "pattern", "source_section": "Pattern", "reusability": "high"}
    note = generate_atomic_note(
        atom, "research/foo.md",
        {"topic": "saas-pricing"},
        "## Pattern\nbody",
    )
    assert "topic: saas-pricing" in note


# ----------------------------------------------------------------------
# Tests — file ops
# ----------------------------------------------------------------------


def test_process_file_skips_nonexistent(tmp_path: Path) -> None:
    result = process_file(tmp_path / "missing.md")
    assert "error" in result


def test_process_file_warns_when_auto_extract_lacks_target(
    tmp_path: Path, reusable_doc: str
) -> None:
    f = tmp_path / "doc.md"
    f.write_text(reusable_doc, encoding="utf-8")
    result = process_file(f, auto_extract=True)
    assert "warning" in result


def test_process_file_writes_representative_atom(
    tmp_path: Path, reusable_doc: str
) -> None:
    src = tmp_path / "doc.md"
    src.write_text(reusable_doc, encoding="utf-8")
    target = tmp_path / "vault" / "auto"

    result = process_file(
        src,
        auto_extract=True,
        target_dir=target,
        source_repo="acme/test",
    )
    assert result["disposition"] == "cross-repo-reusable"
    assert result.get("extracted_files")
    written = list(target.glob("auto-*.md"))
    assert len(written) == 1


def test_scan_directory_finds_md_files(tmp_path: Path, reusable_doc: str) -> None:
    (tmp_path / "a.md").write_text(reusable_doc, encoding="utf-8")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "b.md").write_text("too short", encoding="utf-8")

    results = scan_directory(tmp_path)
    files = {r["file"] for r in results}
    assert any(f.endswith("a.md") for f in files)
    assert any(f.endswith("b.md") for f in files)


def test_process_file_blocks_tmp_paths(reusable_doc: str) -> None:
    p = Path("/tmp/sillok-yeonryun-tmp-guard-test.md")
    try:
        p.write_text(reusable_doc, encoding="utf-8")
        result = process_file(
            p,
            auto_extract=True,
            target_dir=Path("/tmp/sillok-yeonryun-tmp-guard-target"),
        )
        assert "warning" in result
        assert "/tmp/" in result["warning"]
    finally:
        p.unlink(missing_ok=True)
