"""End-to-end smoke: registry load → tier1 match → tier2 fallback.

This exercises the seam between sillok.naru (loading + matching) and the
fact that pack bodies may be absent at install time. It does not invoke
the full retrieval / LLM execution pipeline (those land in later phases).
"""
from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent

import pytest

from sillok.bongsu import patch_telemetry
from sillok.naru import load_registry, tier1_match, tier2_load_full


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    """Tiny vault-style workspace with a registry + 1 real pack body + telemetry."""
    (tmp_path / "packs").mkdir()
    (tmp_path / "packs" / "alpha.md").write_text(
        "# Alpha pack body\nFull contents here.\n",
        encoding="utf-8",
    )
    registry = tmp_path / "packs" / "registry.yaml"
    registry.write_text(
        dedent(
            """
            version: "0.1"
            packs:
              - id: alpha
                title: Alpha pack
                path: packs/alpha.md
                category: domain
                trigger_signals:
                  contains: ["alpha"]
                precedence: 90
              - id: missing-body
                title: Pack without a body
                path: packs/no-such.md
                category: domain
                trigger_signals:
                  contains: ["missing"]
                precedence: 50
            """
        ).strip(),
        encoding="utf-8",
    )
    telemetry = tmp_path / "telemetry.jsonl"
    telemetry.write_text(
        json.dumps({"message_hash": "h1", "knowledge_hit_count": None}) + "\n",
        encoding="utf-8",
    )
    return tmp_path


def test_route_to_telemetry_seam(workspace: Path) -> None:
    registry_path = workspace / "packs" / "registry.yaml"
    packs = load_registry(registry_path)

    candidates = tier1_match("please process alpha workload", packs, top_k=5)
    assert candidates, "tier1 must return at least 1 candidate"
    assert candidates[0]["pack_id"] == "alpha"

    full = tier2_load_full(candidates, packs, repo_root=workspace)
    assert full["loaded_packs"]["alpha"]["loaded"] is True
    assert "missing-body" not in full["loaded_packs"] or (
        full["loaded_packs"].get("missing-body", {}).get("loaded") is False
    )

    # Now patch telemetry as if retrieval ran and produced 0 hits — the
    # post-update path should mark the row with a knowledge gap label.
    patched, row = patch_telemetry(
        workspace / "telemetry.jsonl",
        message_hash="h1",
        hits={
            "knowledge_hit_count": 0,
            "knowledge_hit_paths": [],
            "knowledge_hit_tiers": [],
        },
        pattern_freq=4,
    )
    assert patched is True
    assert row["knowledge_gap_label"] == "no-hits"
    assert row["promotion_candidate"] is True


def test_full_route_with_no_match_returns_empty(workspace: Path) -> None:
    packs = load_registry(workspace / "packs" / "registry.yaml")
    candidates = tier1_match("totally-unrelated-input-quokka", packs, top_k=5)
    assert candidates == []


def test_route_then_overlay_matches_acme(workspace: Path) -> None:
    """Smoke for overlay-style pack injection — adds a packs/registry-overlay.

    We do not fully exercise the overlay merge engine here (covered by
    schemas tests); we just confirm a per-scope add gets surfaced via tier1.
    """
    overlay_pack_dir = workspace / "packs"
    overlay_pack_dir.mkdir(exist_ok=True)
    (overlay_pack_dir / "acme-only.md").write_text(
        "# Acme overlay body\n", encoding="utf-8"
    )
    overlay_registry = workspace / "packs" / "registry-overlay-client-acme.yaml"
    overlay_registry.write_text(
        dedent(
            """
            version: "0.1"
            packs:
              - id: acme-only
                title: Acme overlay pack
                path: packs/acme-only.md
                category: domain
                trigger_signals:
                  contains: ["acme"]
                precedence: 95
            """
        ).strip(),
        encoding="utf-8",
    )
    packs = load_registry(overlay_registry)
    candidates = tier1_match("acme go", packs, top_k=5)
    assert candidates and candidates[0]["pack_id"] == "acme-only"
