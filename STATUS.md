# Sillok — live vs stub matrix

Authoritative status of each [Top 10 Feature](README.md#top-10-features) at the latest published release.
First-time readers — use this page to verify what is shipped before adopting.

- **Released**: `v0.3.0a1` (2026-06-02) — [GitHub Release](https://github.com/sillok-os/sillok/releases/tag/v0.3.0a1) · [PyPI](https://pypi.org/project/sillok/0.3.0a1/) · adds Wave 2 modules + functional `sillok` CLI (previous: `v0.2.0a3`, 2026-05-13)
- **Status legend**: `live` = working code + tests + docs · `partial` = working but missing a documented sub-feature · `stub` = directory or file present, no functional code · `planned` = not yet present

## Feature matrix

| # | Feature | Module(s) | Status | Notes / linked issue |
|---|---|---|:-:|---|
| 1 | Multi-format Auto-Ingest RAG | `pyeonchan` + `janggyeong` | `partial` | `pyeonchan` ships md ingest + watcher; FTS5 indexer deferred to Phase 2. `janggyeong` (corpus store) not yet a module. |
| 2 | Two-Stage Routing | `naru` | `live` | `router_2tier.tier1_match` shipped; Tier 2 LLM classifier live for `route` CLI. |
| 3 | Typed Pack Registry + 5 Retrieval Plans | `jikji` + `bongsu` | `live` | 15 packs in `packs/registry.yaml`. `bongsu` vault search + 5 retrieval plans shipped in `0.1.0a2`. |
| 4 | Proposal-Only 4-Gate Governance | `sangso` | `live` | Lint / Diff / Eval Δ / Approval pipeline shipped in `0.1.0a7` (PR #10, closed #5). |
| 5 | Multi-Tenant Overlay (scoped corpora) | `beopjeon` + `janggyeong` | `planned` | Overlay schema present in `sillok.schemas.overlay`; runtime composition not yet wired. |
| 6 | MCP Bridge | `tongsa` | `live` | 3 tools (`sillok.list_packs` / `sillok.route` / `sillok.search`) shipped in `0.1.0a7` (PR #11, closed #4). |
| 7 | Plugin System | `dure` | `stub` | `sillok/plugins/__init__.py` placeholder only; plugin loader + registry deferred. |
| 8 | Eval Golden Probes + KPI Guard | `gwageo` (`sillok/eval/`) | `live` | 10 probes / 6 families. v1 run: 10/10 pass, 100% citation coverage. CI gate active (`.github/workflows/eval.yml`). Shipped in `0.1.0a7` (PR #9, closed #3). |
| 9 | Cross-Tool Plan SSoT | `madang` + `tongsa` | `live` | `tongsa` MCP bridge live; the unified `sillok` CLI (`sillok/cli/`) is now functional in `0.3.0a1` — `sillok route` + lazy `eval`/`sangso`/`schemas`/`tongsa` dispatch (was a stub raising `ImportError`). |
| 10 | Failure Taxonomy + Replay Pointer | `sagwan` + `gwageo` | `partial` | `gwageo` eval emits `EvalSummary` JSON; `sagwan` (`sillok/telemetry/`) now ships a schema-enforced write-gate (`sillok.telemetry.gate`, `0.3.0a1`). 5-class taxonomy documented in pack bodies, not yet emitted as structured tags. |

## Wave 2 modules (`0.3.0a1`)

Provider-neutral building blocks for observability, governance evidence, and self-growth. All `live` with unit tests; pure/optional-dependency-tolerant.

| Module | Status | Purpose | PR |
|---|:-:|---|---|
| `sillok.telemetry.gate` | `live` | schema-enforced telemetry write-gate (+ `divergence_hook`) | [#17](https://github.com/sillok-os/sillok/pull/17) |
| `sillok.sangso.canary` | `live` | shadow-vs-prod KPI canary → Shadow-stage evidence | [#18](https://github.com/sillok-os/sillok/pull/18) |
| `sillok.yeonryun.coverage` | `live` | coverage-gap detection from router-miss telemetry | [#19](https://github.com/sillok-os/sillok/pull/19) |
| `sillok.eval.calibration` | `live` | Brier routing-confidence calibration | [#20](https://github.com/sillok-os/sillok/pull/20) |
| `sillok.naru.action_layer` | `live` | action axis of 2-D routing (universal taxonomy) | [#21](https://github.com/sillok-os/sillok/pull/21) |
| `sillok.yeonryun.optimizer` | `live` | dependency-free `Optimizer` protocol + reference impl | [#22](https://github.com/sillok-os/sillok/pull/22) |
| `sillok.eval.probe_seeder` | `live` | seed unlabelled probes from conversation logs (redacted) | [#23](https://github.com/sillok-os/sillok/pull/23) |

## Pack registry

- Current count: **25 packs** across 4 sub-categories (`methodology`, `consulting`, `business`/`visual`, `core`)
- Wave 1a (`0.1.0a7`): +5 packs — `meeting-minutes`, `change-management`, `tool-adoption-consulting`, `project-charter`, `infographic-design`
- Wave 1b (`0.2.0a2`): +5 — `consulting-uxui-audit`, `consulting-ai-engineering-audit`, `consulting-security-audit`, `consulting-growth-audit`, `consulting-crossanalysis`
- Wave 1c (`0.2.0a3`): +5 — `pack-maintenance`, `prompt-sequencing-meta`, `agent-1on1`, `worklog`, `everyday-health-symptom`
- Wave 1 (10 → 25 packs) **complete** — see [#1](https://github.com/sillok-os/sillok/issues/1).

## How this page is kept honest

- Each release PR updates this file in the same commit that bumps `pyproject.toml`.
- README Feature 1–10 table cells reference this matrix for live/stub disposition; any claim in README must match a `live` row here.
- A CI drift detector (`STATUS.md` ↔ `packs/registry.yaml` pack-count agreement) is planned — tracked in [#6](https://github.com/sillok-os/sillok/issues/6).
