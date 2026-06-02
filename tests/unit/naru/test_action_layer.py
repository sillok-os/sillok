"""Unit tests for sillok.naru.action_layer — the action axis of 2-D routing."""

from __future__ import annotations

from sillok.naru import action_layer as al


def test_single_action_edit() -> None:
    result = al.classify_action("please shorten this paragraph")
    assert result.top == "edit"
    assert "edit" in result.actions


def test_korean_keyword_matches() -> None:
    result = al.classify_action("이 글을 요약해줘")
    assert result.top == "summarize"


def test_multi_label_ranked_by_score() -> None:
    result = al.classify_action("summarize this and then draw a diagram of it")
    assert set(result.actions) == {"summarize", "diagram"}


def test_no_action_cue_is_empty() -> None:
    result = al.classify_action("the capital of france")
    assert result.actions == []
    assert result.top is None


def test_ascii_word_boundary_avoids_false_positive() -> None:
    # "planet" must not trigger the "plan" action via substring.
    result = al.classify_action("describe a distant planet")
    assert "plan" not in result.actions


def test_taxonomy_override() -> None:
    custom = {"deploy": ["ship", "release", "deploy"]}
    result = al.classify_action("ship the build", taxonomy=custom)
    assert result.top == "deploy"
    # default actions are absent under the override
    assert "edit" not in result.actions


def test_taxonomy_is_universal_not_personal() -> None:
    # Guardrail: the default taxonomy must stay domain-agnostic.
    blob = " ".join(kw for kws in al.DEFAULT_ACTION_TAXONOMY.values() for kw in kws)
    for personal in ("500자", "h5", "ablation", "overleaf", "synology"):
        assert personal not in blob
