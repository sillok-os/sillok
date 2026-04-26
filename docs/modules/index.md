# Modules

Sillok is one Python package with a small, opinionated module layout.
The Korean module names map 1-to-1 to English aliases on the CLI
(see `README.md` §11.1 in the install manual).

| Module | English alias | Top 10 Feature | Source |
|---|---|:-:|---|
| `sillok.naru` | `naru` / `route` | #2 Two-Stage Routing | `sillok/naru/router_2tier.py` |
| `sillok.bongsu` | `bongsu` / `retrieve` | #3 Five Retrieval Plans | `sillok/bongsu/post_update.py` |
| `sillok.jikji` | `jikji` / `packs` | #3 Typed Pack Registry | `sillok/jikji/` (Phase 0 step 2) |
| `sillok.sangso` | `sangso` / `proposal` | #4 4-Gate Governance | `sillok/sangso/` (Phase 1) |
| `sillok.schemas` | (n/a — Pydantic models) | (cross-cutting / Beopjeon) | `sillok/schemas/` |
| `sillok.pyeonchan` | `pyeonchan` / `ingest` | #1 Multi-format Auto-Ingest | `sillok/pyeonchan/{ingest_md,watcher}.py` |
| `sillok.telemetry` | `sagwan` / `telemetry` | #10 Failure Taxonomy + Replay | `sillok/telemetry/` (Phase 1) |
| `sillok.eval` | `gwageo` / `eval` | #8 Eval Probes + KPI | `sillok/eval/` (Phase 1) |
| `sillok.cli` | `madang` / `cli` | (entry point) | `sillok/cli/` |
| `sillok.plugins` | `dure` / `plugins` | #7 Plugin System | `sillok/plugins/` (Phase 1) |

## Two more sub-packages (separate distributions)

| Module | Distribution | Top 10 Feature | Status |
|---|---|:-:|---|
| (Tongsa) MCP bridge | `pip install sillok-tongsa` | #6 MCP Bridge | Phase 1 (PR-D) |
| (Yeokcham) external corpus connector | `pip install sillok-yeokcham-*` | (extension point) | Phase 2+ |

## Module READMEs

Each module has a short README in its source directory:

- [`sillok/naru/README.md`](https://github.com/sillok-os/sillok/blob/main/sillok/naru/README.md)
- [`sillok/bongsu/README.md`](https://github.com/sillok-os/sillok/blob/main/sillok/bongsu/README.md)
- [`sillok/jikji/README.md`](https://github.com/sillok-os/sillok/blob/main/sillok/jikji/README.md)
- [`sillok/sangso/README.md`](https://github.com/sillok-os/sillok/blob/main/sillok/sangso/README.md)
- [`sillok/schemas/README.md`](https://github.com/sillok-os/sillok/blob/main/sillok/schemas/README.md)

## Stability policy

| Surface | Stability |
|---|---|
| `sillok.schemas.*` (Pydantic models) | Field additions forward-compatible; renames require ADR + 1-minor alias deprecation |
| `sillok.naru.tier1_match / tier2_load_full` | Stable from `0.1.0` onward |
| `sillok.bongsu.patch_telemetry` | Stable from `0.1.0` |
| `sillok.pyeonchan.ingest_md / watch_md` | Stable from `0.1.0`; multi-format extends in `0.2.0` |
| Internal helpers (leading underscore) | No stability promise |

## See also

- [Architecture overview](../architecture/README.md)
- [API reference](../api/) — auto-generated from docstrings (planned)
