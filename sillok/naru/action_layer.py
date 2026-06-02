# SPDX-License-Identifier: Apache-2.0
"""sillok.naru.action_layer — the *action* axis of two-dimensional routing.

The two-tier router (:mod:`sillok.naru.router_2tier`) answers *which domain
packs* a message needs. This module answers an orthogonal question: *what is
the user trying to do* — edit, explain, generate, summarize, diagram, review,
or plan. Combining the two gives 2-D routing: ``domain × action``.

The taxonomy here is deliberately **domain-agnostic and universal** — verbs of
work, not the vocabulary of any one project. Each action carries Korean +
English keyword cues; callers may override or extend the taxonomy.

Design — pure, provider-neutral:

- :func:`classify_action` is a heuristic keyword scorer. No model, no network.
- Returns every action that matched, ranked by score, so a message like
  "summarize this and draw a diagram" surfaces both ``summarize`` and
  ``diagram``.

Example::

    from sillok.naru.action_layer import classify_action

    result = classify_action("please shorten this paragraph")
    assert result.top == "edit"
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass, field

#: Universal, domain-agnostic action taxonomy. Keys are stable action ids;
#: values are Korean + English keyword cues (lowercased for matching).
DEFAULT_ACTION_TAXONOMY: dict[str, list[str]] = {
    "edit": [
        "edit",
        "rewrite",
        "revise",
        "polish",
        "shorten",
        "trim",
        "tighten",
        "다듬",
        "수정",
        "줄여",
        "고쳐",
        "퇴고",
    ],
    "explain": [
        "explain",
        "clarify",
        "why",
        "how does",
        "walk through",
        "step by step",
        "설명",
        "왜",
        "어떻게",
        "이해",
        "단계별",
    ],
    "generate": [
        "write",
        "create",
        "draft",
        "generate",
        "compose",
        "build",
        "작성",
        "생성",
        "만들어",
        "초안",
        "써줘",
    ],
    "summarize": [
        "summarize",
        "summary",
        "tldr",
        "condense",
        "key points",
        "recap",
        "요약",
        "정리",
        "핵심",
        "간추",
    ],
    "diagram": [
        "diagram",
        "chart",
        "visualize",
        "graph",
        "flowchart",
        "mermaid",
        "다이어그램",
        "시각화",
        "도식",
        "그래프",
        "그려",
    ],
    "review": [
        "review",
        "audit",
        "critique",
        "check",
        "assess",
        "evaluate",
        "feedback",
        "리뷰",
        "검토",
        "감사",
        "평가",
        "점검",
    ],
    "plan": [
        "plan",
        "roadmap",
        "strategy",
        "steps",
        "outline",
        "approach",
        "milestone",
        "계획",
        "로드맵",
        "전략",
        "단계",
        "기획",
    ],
}


@dataclass(frozen=True)
class ActionMatch:
    action: str
    score: int
    matched_keywords: list[str]


@dataclass
class ActionResult:
    matches: list[ActionMatch] = field(default_factory=list)

    @property
    def top(self) -> str | None:
        return self.matches[0].action if self.matches else None

    @property
    def actions(self) -> list[str]:
        return [m.action for m in self.matches]


def _count(message: str, keyword: str) -> int:
    # Word-boundary match for ASCII cues; substring for CJK (no word boundaries).
    if keyword.isascii():
        return len(re.findall(rf"\b{re.escape(keyword)}\b", message))
    return message.count(keyword)


def classify_action(
    message: str,
    *,
    taxonomy: Mapping[str, list[str]] = DEFAULT_ACTION_TAXONOMY,
) -> ActionResult:
    """Classify a message into one or more universal action types.

    Returns an :class:`ActionResult` whose ``matches`` are ranked by score
    (descending), then by action id for stable ordering. An empty result means
    no action cue was found (the message is domain-only).
    """
    lowered = message.lower()
    matches: list[ActionMatch] = []
    for action, keywords in taxonomy.items():
        hits = [kw for kw in keywords if _count(lowered, kw.lower())]
        if hits:
            score = sum(_count(lowered, kw.lower()) for kw in hits)
            matches.append(ActionMatch(action=action, score=score, matched_keywords=hits))
    matches.sort(key=lambda m: (-m.score, m.action))
    return ActionResult(matches=matches)
