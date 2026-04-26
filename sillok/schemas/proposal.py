"""Proposal artifact schemas — Top 10 Feature #4 (Sangso 4-gate).

These models represent the 5 primary proposal kinds emitted by
``sillok.sangso`` (proposal-only governance). Future phases may add
``compat-edge-add``, ``compat-edge-remove``, ``follow-up-alias``,
``output-contract-split``, ``output-contract-merge``,
``stale-pack-retirement``.

All proposals follow the proposal-only principle: they are written to
``prompts/proposals/`` and require human review before promotion.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from ._base import BaseModel, HAS_PYDANTIC


# ---------------------------------------------------------------------------
# Proposal kinds (base set)
# ---------------------------------------------------------------------------


class MissingIntentProposal(BaseModel):
    """Proposal to add a new prompt pack or trigger signal for an unmatched intent.

    Generated when telemetry analysis finds a cluster of empty-selection
    messages with a coherent verb/noun pattern that no existing pack
    covers. Future MIPROv2-lite extensions can additionally propose a
    draft pack body via LLM.
    """

    id: str
    kind: Literal["missing-intent"] = "missing-intent"
    title: str
    confidence: Literal["low", "medium", "high"]
    evidence: list[str]
    impact_score: float  # 0.0 ~ 1.0, higher = higher priority
    recommended_action: str
    generated_at: datetime
    notes: str | None = None


class ComboProposal(BaseModel):
    """Proposal suggesting that 2+ packs are frequently selected together.

    When the same pack combination appears in telemetry multiple times,
    the router could promote it to a first-class compatibility edge or
    (rarely) a meta-pack.
    """

    id: str
    kind: Literal["combo"] = "combo"
    title: str
    confidence: Literal["low", "medium", "high"]
    pack_ids: list[str]
    frequency: int
    recommended_action: str
    generated_at: datetime
    notes: str | None = None


class DeadSignalProposal(BaseModel):
    """Proposal to prune a trigger signal that never matches any user message.

    If a specific ``trigger_signals.contains`` entry of a pack has 0 hits
    over N days, it is dead weight and should be considered for removal
    or replacement.
    """

    id: str
    kind: Literal["dead-signal"] = "dead-signal"
    title: str
    confidence: Literal["low", "medium", "high"]
    pack_id: str
    signal: str
    days_unused: int
    recommended_action: str
    generated_at: datetime
    notes: str | None = None


class CompatEdgeProposal(BaseModel):
    """Proposal to add or remove a compatibility edge between two packs.

    - ``compat-edge-add``: telemetry shows two packs are frequently
      selected together but the edge is missing from registry.
    - ``compat-edge-remove``: a declared edge has 0 realized activations
      over N days (dead edge cleanup).
    """

    id: str
    kind: Literal["compat-edge-add", "compat-edge-remove"]
    title: str
    confidence: Literal["low", "medium", "high"]
    source_pack: str
    target_pack: str
    evidence_count: int
    recommended_action: str
    generated_at: datetime
    notes: str | None = None


class SkillCandidateProposal(BaseModel):
    """Proposal to promote a repeated workflow into a reusable capability.

    Unlike a regular change-proposal, this does not directly mutate
    canonical prompt assets. It captures evidence that a repeated pack
    combination or operating pattern may deserve a dedicated skill or
    governed capability lane.
    """

    id: str
    kind: Literal["skill-candidate"] = "skill-candidate"
    title: str
    confidence: Literal["low", "medium", "high"]
    candidate_scope: str
    source_signals: list[str]
    evidence: list[str]
    representative_pack_ids: list[str]
    recommended_action: str
    validation_scenarios: list[str]
    miscall_risk: str  # was: false_positive_risk; renamed for clarity
    generated_at: datetime
    notes: str | None = None


# ---------------------------------------------------------------------------
# Registry of known proposal kinds for dispatch
# ---------------------------------------------------------------------------

PROPOSAL_MODELS: dict[str, type[BaseModel]] = {
    "missing-intent": MissingIntentProposal,
    "combo": ComboProposal,
    "dead-signal": DeadSignalProposal,
    "compat-edge-add": CompatEdgeProposal,
    "compat-edge-remove": CompatEdgeProposal,
    "skill-candidate": SkillCandidateProposal,
}


def validate_proposal(payload: dict[str, Any]) -> BaseModel:
    """Dispatch-validate a proposal dict to the correct model.

    Raises ValueError if ``kind`` is unknown or validation fails (Pydantic)
    or if required fields are missing (dataclass fallback).
    """
    kind = payload.get("kind")
    if kind not in PROPOSAL_MODELS:
        raise ValueError(
            f"unknown proposal kind: {kind!r}. "
            f"Expected one of {sorted(PROPOSAL_MODELS.keys())}"
        )
    model_cls = PROPOSAL_MODELS[kind]
    return model_cls.model_validate(payload)  # type: ignore[attr-defined]


__all__ = [
    "MissingIntentProposal",
    "ComboProposal",
    "DeadSignalProposal",
    "CompatEdgeProposal",
    "SkillCandidateProposal",
    "PROPOSAL_MODELS",
    "validate_proposal",
    "HAS_PYDANTIC",
]
