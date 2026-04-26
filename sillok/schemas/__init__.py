"""sillok.schemas — Pydantic / dataclass-fallback schemas.

Public re-exports for the canonical structured contracts used across Sillok:

- ``BaseModel``, ``Field`` (from ``_base``) — Pydantic-first wrapper
- Pack registry schemas (``RegistryPackSchema``, ``RegistrySchema``,
  ``TriggerSignals``, ``RoutingHints``)
- Multi-tenant overlay schemas (``ScopeIdentifier``, ``RegistryOverlay``,
  ``merge_with_global``)
- Proposal artifact schemas (``MissingIntentProposal``, ``ComboProposal``,
  ``DeadSignalProposal``, ``CompatEdgeProposal``, ``SkillCandidateProposal``,
  ``PROPOSAL_MODELS``, ``validate_proposal``)
- Telemetry row schemas (``LegacyTelemetryRow``, ``TelemetryRow`` — OTEL-compatible,
  plus ``InputEnvelope``, ``OutputEnvelope``, ``MetadataEnvelope``,
  ``ScoresEnvelope``, ``ConfidenceBreakdownSchema``, ``CandidateScore``,
  ``RecallHit``)
- Compression configuration (``CompressionConfigSchema``)

See ``adr/0001-initial-architecture-decisions.md`` for the design rationale.
"""
from __future__ import annotations

from ._base import BaseModel, ConfigDict, Field, HAS_PYDANTIC
from .compression import CompressionConfigSchema
from .overlay import RegistryOverlay, ScopeIdentifier, merge_with_global
from .pack import RegistryPackSchema, RegistrySchema, RoutingHints, TriggerSignals
from .proposal import (
    ComboProposal,
    CompatEdgeProposal,
    DeadSignalProposal,
    MissingIntentProposal,
    PROPOSAL_MODELS,
    SkillCandidateProposal,
    validate_proposal,
)
from .telemetry import (
    CandidateScore,
    ConfidenceBreakdownSchema,
    InputEnvelope,
    LegacyTelemetryRow,
    MetadataEnvelope,
    OutputEnvelope,
    RecallHit,
    ScoresEnvelope,
    TelemetryRow,
)

__all__ = [
    "BaseModel",
    "ConfigDict",
    "Field",
    "HAS_PYDANTIC",
    "RegistryPackSchema",
    "RegistrySchema",
    "TriggerSignals",
    "RoutingHints",
    "ScopeIdentifier",
    "RegistryOverlay",
    "merge_with_global",
    "MissingIntentProposal",
    "ComboProposal",
    "DeadSignalProposal",
    "CompatEdgeProposal",
    "SkillCandidateProposal",
    "PROPOSAL_MODELS",
    "validate_proposal",
    "LegacyTelemetryRow",
    "TelemetryRow",
    "CandidateScore",
    "InputEnvelope",
    "OutputEnvelope",
    "MetadataEnvelope",
    "ScoresEnvelope",
    "ConfidenceBreakdownSchema",
    "RecallHit",
    "CompressionConfigSchema",
]
