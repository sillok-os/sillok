"""Unit tests for sillok.schemas.skills_v09 — agentskills.io v0.9 contract."""
from __future__ import annotations

from pathlib import Path

import pytest

from sillok.schemas import SkillsV09Frontmatter
from sillok.schemas.skills_v09 import SkillsV09Frontmatter as DirectImport


def test_skills_v09_minimal() -> None:
    fm = SkillsV09Frontmatter(name="alpha", description="A short summary.")
    assert fm.name == "alpha"
    assert fm.description == "A short summary."
    assert fm.capabilities == []
    assert fm.triggers == []


def test_skills_v09_full() -> None:
    fm = SkillsV09Frontmatter(
        name="pm-enhanced",
        description="PM lifecycle coach — Plan/Doing/Done/Release/Audit.",
        capabilities=["route-pm-message", "emit-lifecycle-artifact"],
        triggers=["[pm]", "$pm-todo"],
    )
    assert fm.name == "pm-enhanced"
    assert "route-pm-message" in fm.capabilities
    assert "[pm]" in fm.triggers


def test_skills_v09_description_max_120() -> None:
    """Description must be ≤ 120 characters (tool-picker constraint)."""
    long_desc = "x" * 121
    with pytest.raises(Exception):
        SkillsV09Frontmatter(name="x", description=long_desc)


def test_skills_v09_name_required() -> None:
    with pytest.raises(Exception):
        SkillsV09Frontmatter(name="", description="ok")


def test_skills_v09_direct_import_matches_reexport() -> None:
    """Re-export from sillok.schemas must be the same class."""
    assert SkillsV09Frontmatter is DirectImport


def test_all_starter_packs_carry_v09_frontmatter() -> None:
    """Every shipped pack body must declare v0.9 frontmatter (acceptance #2)."""
    import yaml

    repo_root = Path(__file__).resolve().parents[3]
    packs_dir = repo_root / "packs"
    pack_files = [
        p
        for p in packs_dir.rglob("*.md")
        if p.name != "README.md"
    ]
    assert pack_files, "no pack body files found"

    for path in pack_files:
        text = path.read_text(encoding="utf-8")
        assert text.startswith("---\n"), f"{path}: missing opening fence"
        rest = text[4:]
        end = rest.find("\n---\n")
        assert end >= 0, f"{path}: missing closing fence"
        block = rest[:end]
        frontmatter = yaml.safe_load(block) or {}

        v09 = {
            key: frontmatter[key]
            for key in ("name", "description", "capabilities", "triggers")
            if key in frontmatter
        }
        assert v09, f"{path}: missing v0.9 fields"
        SkillsV09Frontmatter.model_validate(v09)
