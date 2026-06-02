# SPDX-License-Identifier: Apache-2.0
"""sillok.eval.probe_seeder — seed candidate probes from conversation logs.

Real usage is the best source of eval probes: the questions people actually ask
are the queries the router must handle. This module turns a conversation export
into **unlabelled candidate probe stubs** — redacted first-user-messages from
sufficiently deep conversations — ready for a human to assign the
``expected_pack`` label.

Deliberately *not* in scope (and intentionally dropped from the internal
ancestor): automatic domain/intent labelling. Those labels were derived from one
operator's personal vocabulary and do not generalise; assigning ``expected_pack``
is left to human review.

Design — provider-neutral, privacy-first:

- Input is a generic conversation structure (a list of conversations, each with
  ``messages`` carrying a ``role`` and text). An adapter handles the common
  ``content`` list/str shapes.
- Redaction is a pluggable list of :class:`RedactionRule`. The defaults cover
  *generic* PII (email / phone-like digit runs / URLs) only — no domain- or
  organisation-specific patterns.

Example::

    from sillok.eval.probe_seeder import seed_probes

    stubs = seed_probes(conversations, min_messages=10)
    for stub in stubs:
        print(stub.query)        # redacted
        assert stub.expected_pack is None  # human assigns this
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RedactionRule:
    pattern: re.Pattern[str]
    replacement: str


def _rule(regex: str, replacement: str) -> RedactionRule:
    return RedactionRule(pattern=re.compile(regex), replacement=replacement)


#: Generic PII redactions only — no domain/organisation-specific patterns.
DEFAULT_REDACTIONS: tuple[RedactionRule, ...] = (
    _rule(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "⟨EMAIL⟩"),
    _rule(r"https?://\S+", "⟨URL⟩"),
    _rule(r"\+?\d[\d\-\s().]{7,}\d", "⟨NUMBER⟩"),  # phone-like / long digit runs
)


@dataclass(frozen=True)
class ProbeStub:
    """An unlabelled candidate probe. ``expected_pack`` is for a human to fill."""

    query: str
    source_id: str = ""
    expected_pack: None = None


def redact(text: str, rules: Sequence[RedactionRule] = DEFAULT_REDACTIONS) -> str:
    """Apply every redaction rule to ``text`` in order."""
    for rule in rules:
        text = rule.pattern.sub(rule.replacement, text)
    return text


def _message_text(message: dict[str, Any]) -> str:
    """Extract text from a message across the common export shapes."""
    if message.get("text"):
        return str(message["text"])
    content = message.get("content", "")
    if isinstance(content, list):
        parts = [item.get("text", "") if isinstance(item, dict) else str(item) for item in content]
        return " ".join(p for p in parts if p)
    return str(content)


def _first_user_message(messages: Sequence[dict[str, Any]]) -> str | None:
    for message in messages:
        if message.get("role") == "user":
            text = _message_text(message).strip()
            if text:
                return text
    return None


def seed_probes(
    conversations: Iterable[dict[str, Any]],
    *,
    min_messages: int = 10,
    redactions: Sequence[RedactionRule] = DEFAULT_REDACTIONS,
    max_query_chars: int = 300,
) -> list[ProbeStub]:
    """Turn deep conversations into redacted, unlabelled probe stubs.

    A conversation qualifies when it has at least ``min_messages`` messages and a
    non-empty first user message. The stub's ``query`` is that message, redacted
    and truncated to ``max_query_chars``; ``expected_pack`` is always ``None``.
    """
    stubs: list[ProbeStub] = []
    for conversation in conversations:
        messages = conversation.get("messages") or []
        if len(messages) < min_messages:
            continue
        first = _first_user_message(messages)
        if not first:
            continue
        query = redact(first, redactions)[:max_query_chars].strip()
        if not query:
            continue
        stubs.append(ProbeStub(query=query, source_id=str(conversation.get("id", ""))))
    return stubs
