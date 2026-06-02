# SPDX-License-Identifier: Apache-2.0
"""sillok.yeonryun.coverage — coverage-gap detection from routing telemetry.

The *gap-detection* half of the auto-growth loop. Where
:mod:`sillok.yeonryun.disposition` promotes knowledge that already exists, this
module surfaces what is **missing**: messages the router answered with an empty
pack selection (a coverage gap). It clusters those messages by shared
vocabulary and emits representative trigger candidates — the raw material for a
``sangso`` proposal that adds a new trigger or pack.

Design — provider-neutral, LLM-free (Phase 1):

- Input is a sequence of telemetry rows (plain dicts). Both the v2 envelope
  shape (``input.message`` / ``output.selected_pack_ids``) and the flat legacy
  shape (``message`` / ``selected_pack_ids``) are accepted.
- Clustering is a heuristic n-gram / Jaccard pass — no embeddings, no network.
  A future Phase 2 may add semantic clustering behind the same interface.
- Korean + English tokenisation; stopwords are configurable.

Example::

    from sillok.yeonryun.coverage import find_coverage_gaps

    report = find_coverage_gaps(rows, window_days=7, min_cluster_size=3)
    for cluster in report.clusters:
        print(cluster.size, cluster.trigger_candidates)
"""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any

Row = dict[str, Any]

_KOREAN_TOKEN_RE = re.compile(r"[가-힣]{2,}")
_ENGLISH_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z\-]{2,}")

#: Generic Korean function words filtered by default (not user-specific).
DEFAULT_STOPWORDS: frozenset[str] = frozenset(
    {"있는", "있다", "위해", "하는", "하고", "되는", "이는", "그리고", "또는"}
)


@dataclass(frozen=True)
class EmptyMessage:
    """A routed message that produced an empty pack selection."""

    message: str
    timestamp: str = ""
    message_hash: str = ""


@dataclass(frozen=True)
class GapCluster:
    """A cluster of empty-selection messages sharing vocabulary."""

    size: int
    representative_message: str
    top_tokens: list[str]
    trigger_candidates: list[str]
    sample_messages: list[str]
    message_hashes: list[str]


@dataclass
class CoverageReport:
    total_empty_messages: int
    window_days: int | None
    min_cluster_size: int
    clusters: list[GapCluster] = field(default_factory=list)


def _selection_is_empty(row: Row) -> bool:
    output = row.get("output")
    if isinstance(output, dict):  # v2 envelope shape
        return not output.get("selected_pack_ids")
    return not row.get("selected_pack_ids")  # flat legacy shape


def _message_of(row: Row) -> tuple[str, str]:
    """Return ``(message, message_hash)`` from either schema shape."""
    inp = row.get("input")
    if isinstance(inp, dict):  # v2 envelope shape
        message = inp.get("message") or ""
        message_hash = inp.get("message_hash") or ""
    else:  # flat legacy shape
        message = row.get("message") or ""
        message_hash = row.get("message_hash") or ""
    return str(message).strip(), str(message_hash)


def extract_empty_messages(
    rows: Iterable[Row],
    *,
    window_days: int | None = None,
    now: datetime | None = None,
) -> list[EmptyMessage]:
    """Pull empty-selection messages, optionally within a trailing window."""
    cutoff: datetime | None = None
    if window_days is not None:
        reference = now or datetime.now(UTC)
        cutoff = reference - timedelta(days=window_days)

    found: list[EmptyMessage] = []
    for row in rows:
        if not _selection_is_empty(row):
            continue
        message, message_hash = _message_of(row)
        if not message:
            continue
        timestamp = str(row.get("timestamp", ""))
        if cutoff is not None and not _within_window(timestamp, cutoff):
            continue
        found.append(EmptyMessage(message=message, timestamp=timestamp, message_hash=message_hash))
    return found


def tokenize(message: str, *, stopwords: frozenset[str] = DEFAULT_STOPWORDS) -> list[str]:
    korean = [t for t in _KOREAN_TOKEN_RE.findall(message) if t not in stopwords]
    english = [t.lower() for t in _ENGLISH_TOKEN_RE.findall(message)]
    return korean + english


def cluster_gaps(
    messages: Sequence[EmptyMessage],
    *,
    min_cluster_size: int = 3,
    jaccard_threshold: float = 0.30,
    stopwords: frozenset[str] = DEFAULT_STOPWORDS,
) -> list[GapCluster]:
    """Greedy single-pass clustering by token Jaccard similarity.

    O(n^2) pairwise — adequate for the empty-selection slice (typically n<500).
    """
    tokenised = [(m, set(tokenize(m.message, stopwords=stopwords))) for m in messages]
    assigned = [False] * len(tokenised)
    clusters: list[GapCluster] = []

    for i, (seed, seed_tokens) in enumerate(tokenised):
        if assigned[i] or not seed_tokens:
            continue
        members = [seed]
        token_counts: Counter[str] = Counter(seed_tokens)
        assigned[i] = True
        for j in range(i + 1, len(tokenised)):
            if assigned[j]:
                continue
            other_tokens = tokenised[j][1]
            if not other_tokens:
                continue
            union = seed_tokens | other_tokens
            jaccard = len(seed_tokens & other_tokens) / len(union) if union else 0.0
            if jaccard >= jaccard_threshold:
                members.append(tokenised[j][0])
                token_counts.update(other_tokens)
                assigned[j] = True
        if len(members) >= min_cluster_size:
            top_tokens = [tok for tok, _ in token_counts.most_common(10)]
            clusters.append(
                GapCluster(
                    size=len(members),
                    representative_message=members[0].message[:100],
                    top_tokens=top_tokens,
                    trigger_candidates=top_tokens[:5],
                    sample_messages=[m.message[:80] for m in members[:5]],
                    message_hashes=[m.message_hash for m in members],
                )
            )
    clusters.sort(key=lambda c: -c.size)
    return clusters


def find_coverage_gaps(
    rows: Iterable[Row],
    *,
    window_days: int | None = None,
    min_cluster_size: int = 3,
    jaccard_threshold: float = 0.30,
    stopwords: frozenset[str] = DEFAULT_STOPWORDS,
    now: datetime | None = None,
) -> CoverageReport:
    """End-to-end: telemetry rows → clustered coverage gaps."""
    messages = extract_empty_messages(rows, window_days=window_days, now=now)
    clusters = cluster_gaps(
        messages,
        min_cluster_size=min_cluster_size,
        jaccard_threshold=jaccard_threshold,
        stopwords=stopwords,
    )
    return CoverageReport(
        total_empty_messages=len(messages),
        window_days=window_days,
        min_cluster_size=min_cluster_size,
        clusters=clusters,
    )


def _within_window(timestamp: str, cutoff: datetime) -> bool:
    if not timestamp:
        return True  # undated rows are not excluded by the window
    try:
        parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError:
        return True
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed >= cutoff
