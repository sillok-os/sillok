"""Integration test — bongsu (search) → yeonryun (disposition) seam.

Exercises the end-to-end path:

  1. ``bongsu.build_index`` walks a vault directory.
  2. Notes are filtered by frontmatter (scope/type/tier).
  3. Filtered notes are fed to ``yeonryun.process_file`` for scoring.
  4. Reusable atoms are auto-extracted into a target dir.

This is the contract that makes "vault-resident corpus + auto-growth"
operational. The Karpathy LLM Wiki pattern lives in this seam: bongsu
is the *Query* half, yeonryun is the *Lint / promote* half.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from sillok.bongsu import build_index, filter_notes
from sillok.yeonryun import process_file


REUSABLE_BODY = (
    "# Tiered Pricing Pattern\n\n"
    "## Pattern\n"
    "A reusable workflow for SaaS pricing.\n\n"
    "## Decision Rule\n"
    "Trigger upgrade when seat utilization exceeds 80%.\n\n"
    "## Checklist\n- one\n- two\n- three\n\n"
    "## Best Practice\n"
    "Always tie price to value delivered.\n\n"
    "## Lesson\n"
    "Flat seat pricing leaks revenue at scale.\n\n"
    "| tier | seats | price |\n|---|---|---|\n"
    "| starter | 1-5 | $9 |\n| pro | 6-50 | $29 |\n"
    "| enterprise | 51+ | custom |\n\n"
    "```python\n"
    "def price(seats):\n    ...\n```\n\n"
    "```python\n"
    "def upgrade(plan):\n    ...\n```\n"
) + ("padding text " * 80)


def _md(frontmatter: dict[str, str], body: str) -> str:
    fm_lines = "\n".join(f"{k}: {v}" for k, v in frontmatter.items())
    return f"---\n{fm_lines}\n---\n\n{body}"


@pytest.fixture
def vault_with_results(tmp_path: Path) -> Path:
    vault = tmp_path / "vault"
    vault.mkdir()

    (vault / "alpha.md").write_text(
        _md({
            "title": "Pricing pattern",
            "type": "pattern",
            "scope": "acme",
            "retrieval_tier": "A",
            "tags": "[pricing, b2b]",
        }, REUSABLE_BODY),
        encoding="utf-8",
    )

    (vault / "beta.md").write_text(
        _md({
            "title": "One-off hotfix log",
            "type": "log",
            "scope": "acme",
            "retrieval_tier": "C",
        }, "Quick debug session. Workaround applied. Done.\n"),
        encoding="utf-8",
    )

    (vault / "gamma.md").write_text(
        _md({
            "title": "Pricing pattern (other client)",
            "type": "pattern",
            "scope": "globex",
            "retrieval_tier": "A",
        }, REUSABLE_BODY),
        encoding="utf-8",
    )

    return vault


def test_search_filters_then_disposition_promotes(
    vault_with_results: Path, tmp_path: Path
) -> None:
    """End-to-end: build_index → filter by scope/type → process_file → atom written."""
    notes = build_index(vault_with_results)
    assert len(notes) == 3

    acme_patterns = filter_notes(notes, scope="acme", note_type="pattern", tier="A")
    assert len(acme_patterns) == 1
    assert acme_patterns[0]["title"] == "Pricing pattern"

    target_dir = tmp_path / "promoted"
    promoted: list[dict] = []
    for note in acme_patterns:
        result = process_file(
            note["_abs_path"],
            auto_extract=True,
            target_dir=target_dir,
            vault_root=vault_with_results,
            source_repo="acme/playbooks",
            topic="saas-pricing",
        )
        promoted.append(result)

    [r] = promoted
    assert r["disposition"] == "cross-repo-reusable"
    assert r["score"] >= 6
    assert r.get("extracted_files"), "expected at least one atom file written"

    written = sorted(target_dir.glob("auto-*.md"))
    assert len(written) == 1
    note_text = written[0].read_text(encoding="utf-8")
    assert "source_repo: acme/playbooks" in note_text
    assert "topic: saas-pricing" in note_text
    assert "source-system: sillok.yeonryun" in note_text


def test_seam_skips_low_signal_logs(
    vault_with_results: Path, tmp_path: Path
) -> None:
    """Filter selects logs; disposition correctly classifies them as 'none'."""
    notes = build_index(vault_with_results)
    logs = filter_notes(notes, note_type="log")
    assert len(logs) == 1

    target_dir = tmp_path / "promoted"
    result = process_file(
        logs[0]["_abs_path"],
        auto_extract=True,
        target_dir=target_dir,
        vault_root=vault_with_results,
    )
    assert result["disposition"] == "none"
    assert not result.get("extracted_files")
    assert not list(target_dir.glob("*.md"))


def test_seam_respects_scope_isolation(vault_with_results: Path) -> None:
    """Filtering by scope prevents cross-tenant promotion."""
    notes = build_index(vault_with_results)
    acme_only = filter_notes(notes, scope="acme")
    titles = {n["title"] for n in acme_only}
    assert "Pricing pattern" in titles
    assert "Pricing pattern (other client)" not in titles
