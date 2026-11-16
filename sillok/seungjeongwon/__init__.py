"""sillok.seungjeongwon — context budget (kernel manager 2 of 4) · experimental since 0.4.0.

*Seungjeongwon* (承政院) screened every document before it reached the king.
This manager screens what a prompt hook injects: within one session, a block
shown in the last 30 minutes with identical content is collapsed to a single
pointer line instead of being re-sent every turn.

Why: hooks append pack contracts and recall lines on every turn, and short
follow-up turns inherit the previous turn's packs — so the same contract
block repeats minutes apart. Upstream measurement: 22.4 % of injected pack
contract text in a session was a repeat within 30 minutes. Context is a
finite attention budget; repeats spend it for nothing.

What it never collapses: anything you do not pass through it. By design the
caller passes only *repeatable guidance* (pack contracts, lesson lists) —
coordinates that are an execution contract (asset paths, the applied-pack
line) should bypass it.

Fails open: a corrupt state file, a clock that went backwards, or any error
returns the original block. Reset on compaction/resume with :func:`reset`,
because "the model already saw this" stops being true when context is lost.

Off switch: ``SILLOK_CONTEXT_BUDGET=off``.
"""

from __future__ import annotations

from .budget import (
    DEDUP_WINDOW_S,
    ContextBudget,
    SessionSeen,
    dedup_list_block,
    dedup_sections,
    reset,
)

__all__ = [
    "DEDUP_WINDOW_S",
    "ContextBudget",
    "SessionSeen",
    "dedup_list_block",
    "dedup_sections",
    "reset",
]
