# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project
adheres to [SemVer](https://semver.org/).

## [Unreleased]

### Added
- (none — see 0.1.0a0 below for the latest landed work)

## [0.1.0a0] — 2026-04-26

Pre-alpha checkpoint after the Phase 0 autonomous loop. Cherry-pick + sanitize
of upstream (`aipm`) PromptOS into a clean OSS skeleton; full alpha (`0.1.0a1`)
follows once the remaining Phase 0 step 2 items land.

### Added
- **Skeleton (F0.2)**: directory tree, 9 module stubs, governance/community
  (CONTRIBUTING / GOVERNANCE / CODE_OF_CONDUCT / SECURITY), ADR 0001 (D1~D9),
  `pyproject.toml` (hatchling, 9 optional-dep groups), CI workflows,
  issue / PR templates.
- **Schemas (F0.5)**: `sillok.schemas` with `_base` (Pydantic + stdlib
  fallback), `pack`, `overlay`, `proposal`, `telemetry`, `compression`.
- **Bongsu (F0.4)**: `sillok.bongsu.post_update` — telemetry placeholder
  fill-in with the 5 retrieval plans.
- **Naru 2-tier (F0.3 step 1)**: `sillok.naru.router_2tier` — Tier 1
  keyword + Tier 2 full-body load with shadow-mode dump.
- **Registry (F0.6 step 1)**: `packs/registry.yaml` with 10 starter packs
  (metadata only) and 10 body stubs.
- **Eval fixtures (F0.7)**: `tests/goldens/router-golden.jsonl` (30 entries)
  and `tests/probes/probes.yaml` (17 probes / 6 families).
- **MkDocs site (F0.8)**: `mkdocs.yml` + `docs/index.md` + GitHub Pages
  deploy workflow.
- **CITATION.cff (F0.9)**: software citation + Karpathy gist reference.
- **Pyeonchan (F0.11)**: `sillok.pyeonchan` — md ingest + polling watcher
  (no external dependency) with 4 smoke tests. Multi-format expansion in
  PR-K (Phase 2).

### Notes
- **Not functional yet.** This is a pre-alpha checkpoint. The router can
  parse the registry but the pack bodies are stubs; eval CI runs as
  warn-only; the auto-ingest indexes md only.
- F0.6 step 2 (real pack bodies) and F0.3 step 2 (full v2 router) gate
  the `0.1.0a1` cutover.

## [0.0.1] — 2026-04-26

### Added
- Initial namespace placeholder on PyPI: <https://pypi.org/project/sillok/>
- LICENSE (Apache 2.0), NOTICE (trademark + attribution + cultural references),
  public README (Top 10 features overview, Karpathy / D-series prior art).

### Notes
- 0.0.1 has **no functionality** — it reserves the PyPI name. The first
  functional alpha will be `0.1.0a1`.

## [0.0.1] — 2026-04-26

### Added
- Initial namespace placeholder on PyPI: <https://pypi.org/project/sillok/>
- LICENSE (Apache 2.0), NOTICE (trademark + attribution + cultural references),
  public README (Top 10 features overview, Karpathy / D-series prior art).

### Notes
- 0.0.1 has **no functionality** — it reserves the PyPI name. The first
  functional alpha will be `0.1.0a1`.
- F0.10 in the upstream roadmap remains 🟡 partial until 0.1.0a1 ships.

[Unreleased]: https://github.com/sillok-os/sillok/compare/v0.1.0a0...HEAD
[0.1.0a0]: https://github.com/sillok-os/sillok/releases/tag/v0.1.0a0
[0.0.1]: https://github.com/sillok-os/sillok/releases/tag/v0.0.1
