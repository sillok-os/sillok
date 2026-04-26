# API Reference

This page indexes the public Python API of `sillok`. Auto-generated docs
land via `mkdocstrings` once the dependency is wired into
`mkdocs.yml`; until then, this index lists the surface manually.

> **Heads-up**: anything not listed here (or any name starting with
> `_`) is internal and subject to change without notice.

## `sillok` (top-level)

```python
from sillok import __version__
```

## `sillok.schemas`

Pydantic / dataclass-fallback models. See full documentation in
[`sillok/schemas/README.md`](https://github.com/sillok-os/sillok/blob/main/sillok/schemas/README.md).

```python
from sillok.schemas import (
    BaseModel, Field, ConfigDict, HAS_PYDANTIC,
    RegistryPackSchema, RegistrySchema, TriggerSignals, RoutingHints,
    ScopeIdentifier, RegistryOverlay, merge_with_global,
    MissingIntentProposal, ComboProposal, DeadSignalProposal,
    CompatEdgeProposal, SkillCandidateProposal,
    PROPOSAL_MODELS, validate_proposal,
    LegacyTelemetryRow, TelemetryRow, CandidateScore,
    InputEnvelope, OutputEnvelope, MetadataEnvelope,
    ScoresEnvelope, ConfidenceBreakdownSchema, RecallHit,
    CompressionConfigSchema,
)
```

## `sillok.naru`

```python
from sillok.naru import (
    discovery_tier,        # heuristic for packs without explicit tier
    load_registry,         # read packs/registry.yaml
    tier1_match,           # tier 1 keyword/regex matcher
    tier2_load_full,       # tier 2 full-body loader
    tier_breakdown,        # per-tier capacity stats
    shadow_dump,           # persist routing result for offline diff
)
```

## `sillok.bongsu`

```python
from sillok.bongsu import (
    patch_telemetry,       # fill knowledge_hit_* fields on a routed row
    load_hits,             # convert corpus query JSON → hit summary
)
```

## `sillok.pyeonchan`

```python
from sillok.pyeonchan import (
    Atom,                  # dataclass for an indexed file
    ingest_md,             # walk vault, write index.jsonl
    watch_md,              # polling watcher (Phase 0 bootstrap)
)
```

## CLI commands

```bash
# Routing
sillok route "<message>" [--tier full|summary] [--top-k N] [--json] [--explain]

# Ingest
python -m sillok.pyeonchan.ingest_md <vault>
python -m sillok.pyeonchan.watcher  <vault> [--interval SEC]

# Bongsu post-update
python -m sillok.bongsu.post_update --message-hash <hex> --hits-file <json>
```

## Stability

See [`docs/modules/`](../modules/) for the stability policy across each
module surface.

## See also

- [Modules](../modules/)
- [Architecture](../architecture/README.md)
- [Tutorials](../tutorials/) and [Recipes](../recipes/)
