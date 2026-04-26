"""Smoke tests for sillok.naru — two-stage routing."""
from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest

from sillok.naru import (
    discovery_tier,
    load_registry,
    tier1_match,
    tier2_load_full,
    tier_breakdown,
)


@pytest.fixture
def registry_path(tmp_path: Path) -> Path:
    """Minimal registry.yaml fixture with 3 packs."""
    p = tmp_path / "registry.yaml"
    p.write_text(
        dedent(
            """
            version: "0.1"
            packs:
              - id: alpha
                title: Alpha pack
                path: packs/alpha.md
                category: domain
                trigger_signals:
                  explicit: ["[alpha]"]
                  contains: ["alpha"]
                precedence: 90
                summary_overlay: ["alpha summary"]
              - id: beta
                title: Beta pack
                path: packs/beta.md
                category: workflow
                trigger_signals:
                  contains: ["beta", "bravo"]
                precedence: 50
                summary_overlay: ["beta summary"]
              - id: zulu
                title: Zulu pack (archived)
                path: packs/zulu.md
                category: domain
                status: archived
                trigger_signals:
                  contains: ["zulu"]
                precedence: 10
            """
        ).strip(),
        encoding="utf-8",
    )
    return p


def test_load_registry_returns_packs(registry_path: Path) -> None:
    packs = load_registry(registry_path)
    assert len(packs) == 3
    assert packs[0]["id"] == "alpha"


def test_tier1_match_explicit_outranks_keyword(registry_path: Path) -> None:
    packs = load_registry(registry_path)
    candidates = tier1_match("[alpha] please run with bravo too", packs, top_k=5)
    ids = [c["pack_id"] for c in candidates]
    assert ids[0] == "alpha"
    assert "beta" in ids


def test_tier1_skips_archived_packs(registry_path: Path) -> None:
    packs = load_registry(registry_path)
    candidates = tier1_match("zulu zulu zulu", packs, top_k=5)
    ids = {c["pack_id"] for c in candidates}
    assert "zulu" not in ids


def test_discovery_tier_heuristic() -> None:
    assert discovery_tier({"discovery_tier": "summary"}) == "summary"
    assert discovery_tier({"precedence": 95}) == "full"
    assert discovery_tier({"last_used_12d": 7}) == "full"
    assert discovery_tier({"precedence": 10}) == "summary"


def test_tier_breakdown_shape(registry_path: Path) -> None:
    packs = load_registry(registry_path)
    bd = tier_breakdown(packs)
    assert "tier_counts" in bd
    assert bd["tier_counts"]["summary"] + bd["tier_counts"]["full"] == 3


def test_tier2_handles_missing_body(tmp_path: Path, registry_path: Path) -> None:
    packs = load_registry(registry_path)
    candidates = tier1_match("alpha", packs, top_k=5)
    result = tier2_load_full(candidates, packs, repo_root=tmp_path)
    loaded = result["loaded_packs"].get("alpha", {})
    assert loaded.get("loaded") is False
    assert loaded.get("reason") == "missing"
