"""Telemetry row schemas — Top 10 Feature #10 (Sagwan).

Two formats supported in parallel for migration safety:

- **Legacy 6-field row** (``LegacyTelemetryRow``) — the original JSONL format.
- **OTEL-compatible span event** (``TelemetryRow``) — trace_id, scores,
  metadata. New rows are written in this format.

Routers gradually cut over: legacy rows remain in place; new rows land in
the OTEL-compatible schema and are exported to OpenTelemetry / Langfuse /
Datadog when ``SILLOK_OTEL=1`` is set.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from ._base import BaseModel, HAS_PYDANTIC


# ---------------------------------------------------------------------------
# Legacy schema
# ---------------------------------------------------------------------------


class LegacyTelemetryRow(BaseModel):
    """Schema for legacy ``.sillok/telemetry.jsonl`` entries.

    This is the minimal 6-field format produced by older routers. New
    rows are no longer written in this format; legacy rows continue to
    validate.
    """

    timestamp: str  # ISO 8601 string
    message: str
    selected_pack_ids: list[str]
    selected_categories: list[str]
    confidence: Literal["low", "medium", "high"]
    applied_prompt_packs_line: str


# ---------------------------------------------------------------------------
# OTEL-compatible schema
# ---------------------------------------------------------------------------


class CandidateScore(BaseModel):
    """Individual pack candidate score within a routing decision."""

    id: str
    score: float
    reasons: list[str] = []


class InputEnvelope(BaseModel):
    """Input context for a routing decision."""

    message: str
    message_hash: str | None = None
    message_length: int | None = None
    context_hash: str | None = None


class OutputEnvelope(BaseModel):
    """Output of a routing decision."""

    selected_pack_ids: list[str]
    selected_categories: list[str]
    confidence_label: Literal["low", "medium", "high"]
    applied_prompt_packs_line: str
    pack_reason_codes: list[str] = []


class MetadataEnvelope(BaseModel):
    """Metadata attached to the routing trace."""

    registry_version: str | None = None  # sha256 of packs/registry.yaml
    router_version: str | None = None    # e.g. "v2"
    pack_versions: dict[str, str] = {}
    output_contracts_expected: list[str] = []
    output_contracts_passed: bool | None = None
    probe_type: Literal["production", "probe", "shadow", "unittest"] = "production"
    error_class: str | None = None


class ConfidenceBreakdownSchema(BaseModel):
    """Structured confidence calibration breakdown."""

    margin_raw: float = 0.0
    margin_normalized: float = 0.0
    prior: float = 0.0
    coverage: float = 0.0
    final_score: float = 0.0
    label: str = "low"
    version: str = "v3"


class RecallHit(BaseModel):
    """A single recall search result from the FTS5 session index."""

    source_type: str = "telemetry"  # telemetry | result | session
    content_preview: str = ""
    relevance_score: float = 0.0
    timestamp: str = ""
    pack_ids: list[str] = []


class ScoresEnvelope(BaseModel):
    """Calibrated scores attached to the routing trace."""

    confidence_score: float | None = None  # 0.0 ~ 1.0
    semantic_top_score: float | None = None
    margin: float | None = None
    user_feedback: dict[str, Any] | None = None  # {rating, edited, final_action}
    confidence_breakdown: dict[str, Any] | None = None


class TelemetryRow(BaseModel):
    """OTEL-compatible telemetry row.

    Compatible with OpenTelemetry span events and Langfuse trace ingestion.
    """

    trace_id: str  # uuid or hex
    span_id: str | None = None
    session_id: str | None = None
    actor: Literal["human", "claude", "codex", "system", "unittest"] = "human"
    event_name: str = "sillok.route"
    timestamp: datetime
    input: InputEnvelope
    output: OutputEnvelope
    metadata: MetadataEnvelope
    scores: ScoresEnvelope
    candidate_scores: list[CandidateScore] = []
    latency_ms: int = 0
    tokens_in: int = 0
    tokens_out: int = 0
    usd_cost: float = 0.0
    # Learning trigger fields
    tool_call_count: int = 0
    error_recovery_detected: bool = False
    user_correction_detected: bool = False


__all__ = [
    "LegacyTelemetryRow",
    "TelemetryRow",
    "CandidateScore",
    "InputEnvelope",
    "OutputEnvelope",
    "MetadataEnvelope",
    "ScoresEnvelope",
    "ConfidenceBreakdownSchema",
    "RecallHit",
    "HAS_PYDANTIC",
]
