"""Unit tests for sillok.tongsa.tools — pure tool logic + reason codes."""
from __future__ import annotations

from sillok.tongsa.tools import (
    REASON_CODES,
    classify_reason_codes,
    sillok_list_packs,
    sillok_route,
)


# ---------------------------------------------------------------------------
# Reason codes
# ---------------------------------------------------------------------------

def test_reason_codes_have_seven_entries() -> None:
    assert set(REASON_CODES) == {"R1", "R2", "R3", "R4", "R5", "R6", "R7"}


def test_classify_explicit_trigger() -> None:
    candidate = {
        "pack_id": "pm-enhanced",
        "score": 209.5,
        "reasons": ["explicit:[pm]"],
        "tier": "full",
    }
    codes = classify_reason_codes(candidate)
    assert "R1" in codes
    assert "R3" in codes  # score > 0 includes precedence
    assert "R4" in codes  # tier=full
    assert "R2" not in codes


def test_classify_keyword_only() -> None:
    candidate = {
        "pack_id": "risk-uncertainty",
        "score": 50.0,
        "reasons": ["keyword:risk register,EMV"],
        "tier": "summary",
    }
    codes = classify_reason_codes(candidate)
    assert "R2" in codes
    assert "R3" in codes
    assert "R1" not in codes
    assert "R4" not in codes


def test_classify_precedence_only() -> None:
    candidate = {
        "pack_id": "high-precedence",
        "score": 10.0,
        "reasons": [],
        "tier": "summary",
    }
    codes = classify_reason_codes(candidate)
    assert codes == ["R3"]


def test_classify_dedupes_codes() -> None:
    candidate = {
        "pack_id": "x",
        "score": 250.0,
        "reasons": ["explicit:[pm]", "explicit:$pm-todo", "keyword:milestone,issue"],
        "tier": "full",
    }
    codes = classify_reason_codes(candidate)
    assert len(codes) == len(set(codes))
    assert "R1" in codes and "R2" in codes


# ---------------------------------------------------------------------------
# sillok.list_packs
# ---------------------------------------------------------------------------

def test_list_packs_returns_all_starter_packs() -> None:
    packs = sillok_list_packs()
    ids = {p["id"] for p in packs}
    assert "pm-enhanced" in ids
    assert "risk-uncertainty" in ids
    assert len(packs) >= 10


def test_list_packs_payload_shape() -> None:
    packs = sillok_list_packs()
    sample = packs[0]
    expected = {
        "id",
        "title",
        "category",
        "sub_category",
        "precedence",
        "visibility_label",
        "summary_overlay",
        "intent_tags",
        "output_contracts",
    }
    assert set(sample.keys()) >= expected


# ---------------------------------------------------------------------------
# sillok.route
# ---------------------------------------------------------------------------

def test_route_finds_pm_enhanced_for_pm_trigger() -> None:
    result = sillok_route("[pm] kickoff a new feature", top_k=3)
    assert result["packs"]
    top = result["packs"][0]
    assert top["pack_id"] == "pm-enhanced"
    assert "R1" in result["reason_codes"]


def test_route_finds_risk_pack_for_risk_phrase() -> None:
    result = sillok_route("build a risk register with EMV", top_k=3)
    assert result["packs"]
    top_ids = [p["pack_id"] for p in result["packs"]]
    assert "risk-uncertainty" in top_ids
    assert "R2" in result["reason_codes"]


def test_route_no_match_emits_r7() -> None:
    result = sillok_route("zzzzzz nonsense unmatched gibberish", top_k=3)
    assert result["packs"] == []
    assert result["reason_codes"] == ["R7"]


def test_route_top_k_truncation_emits_r6() -> None:
    # A query that matches several packs ("triangulation" hits report-quality;
    # let's craft a multi-match): use a generic single-keyword that several packs
    # contain. Use top_k=1 so truncation is forced when ≥2 candidates exist.
    result = sillok_route("Pyramid Principle 1-pager Sequoia", top_k=1)
    if len(result["packs"]) == 1 and len(sillok_list_packs()) > 1:
        # R6 only triggers when total_packs > top_k AND len(candidates) == top_k
        assert "R6" in result["reason_codes"]


def test_route_payload_shape() -> None:
    result = sillok_route("[pm] release", top_k=2)
    assert "packs" in result
    assert "reason_codes" in result
    if result["packs"]:
        cand = result["packs"][0]
        assert {"pack_id", "score", "reasons", "reason_codes", "tier", "category"} <= set(cand.keys())
