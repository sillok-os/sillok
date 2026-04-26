"""Smoke tests for sillok.schemas — Pydantic + stdlib fallback contracts."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from sillok.schemas import (
    HAS_PYDANTIC,
    InputEnvelope,
    LegacyTelemetryRow,
    MetadataEnvelope,
    OutputEnvelope,
    PROPOSAL_MODELS,
    RegistryOverlay,
    RegistryPackSchema,
    RegistrySchema,
    ScopeIdentifier,
    ScoresEnvelope,
    TelemetryRow,
    TriggerSignals,
    merge_with_global,
    validate_proposal,
)


def test_registry_pack_schema_minimal() -> None:
    pack = RegistryPackSchema(
        id="alpha",
        title="Alpha",
        path="packs/alpha.md",
        category="domain",
    )
    assert pack.id == "alpha"
    assert pack.precedence == 0
    assert isinstance(pack.trigger_signals, TriggerSignals)


def test_registry_schema_validates_pack_list() -> None:
    payload = {
        "version": "0.1",
        "packs": [
            {
                "id": "alpha",
                "title": "Alpha",
                "path": "packs/alpha.md",
                "category": "domain",
            }
        ],
    }
    registry = RegistrySchema.model_validate(payload)
    assert len(registry.packs) == 1


def test_scope_identifier_render() -> None:
    assert ScopeIdentifier(kind="global").render() == "global"
    assert (
        ScopeIdentifier(kind="client", value="acme").render() == "client:acme"
    )


def test_overlay_merge_add_override_hide() -> None:
    base_pack = RegistryPackSchema(
        id="base", title="Base", path="x", category="domain"
    )
    add_pack = RegistryPackSchema(
        id="extra", title="Extra", path="y", category="domain"
    )
    override_pack = RegistryPackSchema(
        id="base", title="Base (overridden)", path="x", category="domain"
    )
    overlay = RegistryOverlay(
        version="0.1",
        scope=ScopeIdentifier(kind="client", value="acme"),
        add=[add_pack],
        override=[override_pack],
        hide=["nope"],
    )
    merged = merge_with_global(overlay, [base_pack])
    titles = {p.id: p.title for p in merged}
    assert titles["base"] == "Base (overridden)"
    assert titles["extra"] == "Extra"


def test_overlay_none_returns_global_unchanged() -> None:
    base_pack = RegistryPackSchema(
        id="base", title="Base", path="x", category="domain"
    )
    merged = merge_with_global(None, [base_pack])
    assert merged == [base_pack]


def test_validate_proposal_dispatches_to_correct_model() -> None:
    payload = {
        "id": "p1",
        "kind": "missing-intent",
        "title": "Missing pricing pack",
        "confidence": "medium",
        "evidence": ["3 unmatched messages"],
        "impact_score": 0.7,
        "recommended_action": "Draft 'pricing' pack",
        "generated_at": datetime.now(timezone.utc),
    }
    proposal = validate_proposal(payload)
    assert proposal.kind == "missing-intent"
    assert proposal.title.startswith("Missing")


def test_validate_proposal_rejects_unknown_kind() -> None:
    with pytest.raises(ValueError):
        validate_proposal({"kind": "not-a-real-kind", "id": "x"})


def test_proposal_models_registry_covers_5_kinds() -> None:
    expected = {
        "missing-intent",
        "combo",
        "dead-signal",
        "compat-edge-add",
        "compat-edge-remove",
        "skill-candidate",
    }
    assert expected.issubset(set(PROPOSAL_MODELS))


def test_legacy_telemetry_row_roundtrip() -> None:
    row = LegacyTelemetryRow(
        timestamp="2026-04-26T00:00:00Z",
        message="hello",
        selected_pack_ids=["alpha"],
        selected_categories=["domain"],
        confidence="high",
        applied_prompt_packs_line="applied prompt packs: alpha",
    )
    dumped = row.model_dump()
    assert dumped["confidence"] == "high"


def test_telemetry_row_otel_compatible() -> None:
    row = TelemetryRow(
        trace_id="t1",
        timestamp=datetime.now(timezone.utc),
        input=InputEnvelope(message="hi"),
        output=OutputEnvelope(
            selected_pack_ids=["alpha"],
            selected_categories=["domain"],
            confidence_label="high",
            applied_prompt_packs_line="applied prompt packs: alpha",
        ),
        metadata=MetadataEnvelope(),
        scores=ScoresEnvelope(),
    )
    assert row.event_name == "sillok.route"
    assert row.actor == "human"


def test_has_pydantic_is_bool() -> None:
    assert isinstance(HAS_PYDANTIC, bool)
