"""Tier-1 matching rules (0.3.1).

Two defects observed in a real install (2026-11-15):
- every pack with a non-zero ``precedence`` was returned for any message,
  so an unrelated request still loaded pack bodies;
- upper-case abbreviations matched inside ordinary words
  (``SK`` in ``risk``, ``SCR`` in ``script``).
"""

from __future__ import annotations

from typing import Any

from sillok.naru import tier1_match
from sillok.naru.router_2tier import keyword_hit


def _pack(pack_id: str, contains: list[str], precedence: int = 50, **extra: Any) -> dict[str, Any]:
    return {
        "id": pack_id,
        "path": f"packs/{pack_id}.md",
        "trigger_signals": {"contains": contains, **extra},
        "precedence": precedence,
    }


def test_unmatched_pack_is_never_a_candidate() -> None:
    packs = [_pack("high-precedence", ["charter"], precedence=99)]
    assert tier1_match("weather tomorrow?", packs) == []


def test_precedence_only_breaks_ties_between_matched_packs() -> None:
    packs = [
        _pack("low", ["risk"], precedence=10),
        _pack("high", ["risk"], precedence=90),
        _pack("unrelated", ["invoice"], precedence=99),
    ]
    ids = [c["pack_id"] for c in tier1_match("update the risk log", packs)]
    assert ids == ["high", "low"]


def test_explicit_trigger_still_wins() -> None:
    packs = [
        _pack("keyword", ["deck"], precedence=90),
        _pack("tagged", [], precedence=10, explicit=["/deck"]),
    ]
    assert tier1_match("/deck for the board", packs)[0]["pack_id"] == "tagged"


def test_abbreviation_does_not_match_inside_words() -> None:
    assert not keyword_hit("SK", "assess the risk register")
    assert not keyword_hit("SCR", "fix the build script")
    assert not keyword_hit("PMC", "apmc")


def test_abbreviation_matches_as_token_any_case_and_before_cjk_particles() -> None:
    assert keyword_hit("SK", "SK workshop plan")
    assert keyword_hit("RTM", "update the rtm today")
    assert keyword_hit("RTM", "RTM을 갱신")
    assert keyword_hit("PMC", "(PMC) draft")


def test_lowercase_keywords_keep_substring_semantics() -> None:
    assert keyword_hit("risk", "list the risks")
    assert keyword_hit("회의록", "오늘 회의록 정리")
    assert keyword_hit("risk register", "Risk Register review")
