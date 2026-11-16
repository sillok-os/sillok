"""sillok.chunchugwan — prompt-time memory recall (kernel manager 3 of 4) · experimental since 0.4.0.

*Chunchugwan* (春秋館) kept the state records. This manager indexes memory
notes (Markdown with front matter, one chunk per heading path) and past
episodes (JSONL of prompt → artifact, corrected?) in SQLite FTS5, and at
prompt time returns at most 5 lines / 900 bytes of *pointers* — paths and a
redacted one-line description, never note bodies or full prompts.

Why: in the upstream harness 39 % of memory notes had not been opened in 30
days, because the only route to them was a one-line index loaded every
session; and 9,492 episodes were recorded but not searchable. Measured
recall@3 against actual later opens started at 34 % — treat this module as a
retrieval path to measure, not a solved problem.

Guards: per-source ranking, a title/heading-match gate, Korean particle
stripping, opt-out tags, a 0.25 s refresh budget inside hooks, and an
exposure log of IDs only (so "shown, then opened" can be measured).
Off switch: ``SILLOK_MEMORY_RECALL=off``.
"""

from __future__ import annotations

from .recall import (
    chunk_note,
    connect,
    eligible_episode,
    hook_block,
    query_terms,
    redact,
    refresh_episodes,
    refresh_memory,
    render_block,
    search,
)

__all__ = [
    "chunk_note",
    "connect",
    "eligible_episode",
    "hook_block",
    "query_terms",
    "redact",
    "refresh_episodes",
    "refresh_memory",
    "render_block",
    "search",
]
