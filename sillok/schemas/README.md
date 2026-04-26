# sillok.schemas

This directory holds the **structured output contracts** for Sillok, encoded as Python models.

It implements the **Beopjeon (법전)** layer in the module reference — Pydantic-first with a stdlib dataclass fallback so the core can run even without Pydantic installed.

## Module map

| File | Purpose |
|---|---|
| `_base.py` | `BaseModel` + `Field` + `ConfigDict` — Pydantic 2.x wrapper with stdlib fallback (no Pydantic dependency required for the core to import). |
| `pack.py` | `RegistryPackSchema`, `RegistrySchema`, `TriggerSignals`, `RoutingHints` — validates `packs/registry.yaml` (Top 10 Feature #3). |
| `overlay.py` | `ScopeIdentifier`, `RegistryOverlay`, `merge_with_global` — multi-tenant scope overlay (Feature #5). |
| `proposal.py` | 5 proposal kinds + `validate_proposal` dispatcher — Sangso 4-gate governance artifacts (Feature #4). |
| `telemetry.py` | `LegacyTelemetryRow` + OTEL-compatible `TelemetryRow` (with `InputEnvelope`, `OutputEnvelope`, `MetadataEnvelope`, `ScoresEnvelope`, etc.) — Feature #10. |
| `compression.py` | `CompressionConfigSchema` — context compaction thresholds. |
| `__init__.py` | Public re-exports. |

## Pydantic vs fallback

```python
from sillok.schemas import BaseModel, Field, HAS_PYDANTIC

if HAS_PYDANTIC:
    # Full Pydantic 2.x validation, error messages, JSON schema generation, etc.
    ...
else:
    # stdlib dataclass shim — init-only, no validation, but the core still works.
    ...
```

The fallback covers what `sillok` core needs: typed init, `model_dump()`, `model_dump_json()`, `model_validate()`, list / dict / `BaseModel` field coercion, and clear errors on unknown / missing fields.

## Validating a registry on disk

```python
import yaml
from sillok.schemas import RegistrySchema

with open("packs/registry.yaml") as f:
    payload = yaml.safe_load(f)

registry = RegistrySchema.model_validate(payload)
print(f"loaded {len(registry.packs)} packs (version {registry.version})")
```

If Pydantic is installed, validation errors are field-precise. Without Pydantic, missing required fields raise `TypeError` and unknown fields raise `TypeError(f"unexpected field(s): ...")`.

## Validating a proposal artifact

```python
import json
from sillok.schemas import validate_proposal

with open("prompts/proposals/2026-04-26-missing-intent-pricing.json") as f:
    payload = json.load(f)

proposal = validate_proposal(payload)
print(f"{proposal.kind}: {proposal.title} (confidence={proposal.confidence})")
```

`validate_proposal` dispatches to the correct sub-model based on `payload["kind"]`. Unknown kinds raise `ValueError`.

## Stability policy

- Field **additions** are forward-compatible: existing payloads continue to validate.
- Field **renames** require an ADR and a migration path (legacy field kept as alias for one minor release).
- Field **removals** require a major-version bump.
