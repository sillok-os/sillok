# Tutorials

Hands-on, step-by-step guides. Each tutorial is self-contained and runs
in 10 ~ 30 minutes.

> **Status (2026-04-26)**: tutorial pages are populated as the
> corresponding modules ship. Use `examples/starter-projects/` for
> runnable equivalents until the polished narratives land here.

## Planned

| # | Title | Status |
|:-:|---|:-:|
| 01 | Minimal install and first route | 🟡 (covered in `examples/minimal/`) |
| 02 | Multi-pack composition + quality guard | 🟡 (covered in `examples/multi-pack/`) |
| 03 | Multi-tenant overlays | 🟡 (covered in `examples/multi-tenant/`) |
| 04 | Multi-format auto-ingest with watch | ⏳ (after PR-K Phase 2) |
| 05 | MCP integration in Claude Code | ⏳ (after PR-D Phase 1) |
| 06 | Eval golden probes in CI | ⏳ (after PR-B Phase 1) |
| 07 | Authoring a new pack | ⏳ |
| 08 | Custom corpus connector via Yeokcham | ⏳ |

## Conventions

Each tutorial follows this template:

```markdown
# Tutorial NN — <Title>

## Goal

One sentence describing what the reader will achieve.

## Prerequisites

- ...

## Steps

```bash
# numbered, copy-pasteable shell blocks
```

## Verification

How to confirm the tutorial succeeded.

## Cleanup

How to undo any state the tutorial created.
```

## See also

- [Recipes](../recipes/) — short, single-purpose snippets
- [Architecture](../architecture/README.md) — design context
