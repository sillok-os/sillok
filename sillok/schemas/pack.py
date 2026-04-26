"""Registry pack schema — Pydantic validation for ``packs/registry.yaml``.

This module defines the canonical typed contract for a single pack entry.
It is consumed by ``sillok.jikji`` (the typed pack registry, Top 10 Feature #3)
and by CI lint that validates ``packs/registry.yaml`` before merge.

It also supports:

- Proposing new pack definitions with field-level validation
  (Top 10 Feature #4 — Sangso 4-gate)
- Phase 1 ``routing_hints`` / ``trigger_examples`` extended fields
  (used by Router v2 — ``sillok.naru``)
"""
from __future__ import annotations

from typing import Literal

from ._base import BaseModel, HAS_PYDANTIC


class TriggerSignals(BaseModel):
    """Trigger signal sub-schema for a pack."""

    explicit: list[str] = []
    contains: list[str] = []


class RoutingHints(BaseModel):
    """Phase 1 routing_hints extension fields (optional).

    Forward-compatible: packs without routing_hints continue to validate
    against the base registry schema.
    """

    generic_verbs: list[str] = []
    followup_aliases: list[str] = []
    requires_context: bool = False
    max_repeat_penalty: float = 0.0


class RegistryPackSchema(BaseModel):
    """Validation model for a single pack entry in ``packs/registry.yaml``.

    Mirrors the runtime ``PromptPack`` dataclass used by ``sillok.jikji`` with
    Pydantic field-level validation. Optional fields match registry schema
    variability across releases.
    """

    id: str
    title: str
    path: str
    category: Literal["domain", "workflow", "output-style", "follow-up", "quality-guard"]
    # sub_category (forward-compatible) — used to re-partition the "workflow"
    # category into themed sub-namespaces. Existing entries without
    # sub_category remain valid.
    # Suggested values:
    #   "consulting" / "methodology" / "standard" / "publishing" /
    #   "orchestration" / "image" / "claude-code" / "compliance"
    sub_category: str | None = None
    trigger_signals: TriggerSignals = TriggerSignals()
    intent_tags: list[str] = []
    output_contracts: list[str] = []
    precedence: int = 0
    compatible_with: list[str] = []
    conflicts_with: list[str] = []
    visibility_label: str = ""
    summary_overlay: list[str] = []

    # Phase 1 extension fields (optional, forward-compatible)
    routing_hints: RoutingHints | None = None
    trigger_examples: list[str] = []

    # Progressive disclosure fields
    token_estimate: int = 0
    level0_summary: str = ""


class RegistrySchema(BaseModel):
    """Top-level ``packs/registry.yaml`` schema wrapper."""

    version: str
    packs: list[RegistryPackSchema]


__all__ = [
    "TriggerSignals",
    "RoutingHints",
    "RegistryPackSchema",
    "RegistrySchema",
    "HAS_PYDANTIC",
]
