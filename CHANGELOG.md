# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project
adheres to [SemVer](https://semver.org/).

## [Unreleased]

### Added
- (none yet — pending F0.3 step 2 cherry-pick of full v2 router with
  semantic embeddings + calibration, deferred to 0.2.0; also pending
  FTS5 indexer for `pyeonchan` Phase 2)

## [0.1.0a6] — 2026-04-27

Documentation release. README structural reorganization only — no
code, no API, no test changes. Behaviorally identical to 0.1.0a5
at runtime.

### Changed
- **READMEs (EN + KO) reorganized into a 6-part flow** matching the
  natural reading order (value → use cases → install → use →
  maintain → appendix):
  1. **Part 1 — Value & Overview** — What you get, Architecture
     (Business + Technical views), Framework coverage, Top 10
     features.
  2. **Part 2 — Business Use Cases** — Persona pairing (find your
     category fast), Common workflows (3 archetypes).
  3. **Part 3 — Installation** — Requirements, GA Quickstart,
     Setup paths (Basic / MCP / RAG corpus).
  4. **Part 4 — Usage** — Consultant Quickstart for 0.1.0a6 (the
     5-step ABCDE today path), Common commands, What does NOT yet
     ship.
  5. **Part 5 — Maintenance & Extension** — Troubleshooting,
     Multi-user deployment, **Adding a pack for your domain**,
     Module reference.
  6. **Part 6 — Appendix** — License, Prior art (Karpathy LLM Wiki
     + D-series), Citation.
- Top-of-README **Reading order** TOC links the six parts.
- Version references updated `0.1.0a3` → `0.1.0a6` throughout the
  Consultant Quickstart, Mermaid Business view label, framework
  coverage table headers, and gap table.
- Module reference table includes the new `bongsu / vault search`
  and `yeonryun / atom promotion` summaries delivered in 0.1.0a2.

### Why a docs-only patch alpha
Earlier alphas accumulated sections in the order they were authored
(`Quickstart → Consultant Quickstart → Architecture → Framework
coverage → What you get → Requirements → Setup → Workflows → ...`).
A first-time reader hits *install before value* and *examples
before persona*. The 6-part flow puts value first, persona second,
install third — matching how a consultant evaluates whether to
adopt the tool.

`pip install "sillok==0.1.0a5"` and `pip install "sillok==0.1.0a6"`
are behaviorally identical at runtime.

## [0.1.0a5] — 2026-04-27

Documentation release. No code changes; new contribution guide and
README cross-links only. Behaviorally identical to 0.1.0a4 at runtime.

### Added
- **`docs/contributing/extending-with-your-domain.md`** — single-page
  guide for both contribution paths (external contributor + maintainer
  SME). Covers:
  1. What to add — pack vs. category vs. body vs. revision (with
     effort estimates)
  2. Pack anatomy — required frontmatter v1, body sections (Role,
     Methodology, Output format, Constraints, Examples, Reason codes)
  3. registry.yaml entry — required keys + schema validation
  4. **Sanitization checklist** (5 categories: client identifiers,
     confidential numbers, internal URLs, closed methodology IP,
     jurisdiction-locked compliance) — most common reason a PR
     gets sent back
  5. Standards citation rule — nominative fair use boilerplate +
     `NOTICE` append discipline
  6. Framework coverage inventory update — README + framework-
     coverage.md must move together
  7. **5-step quality gate** — schema/registry validation,
     sanitization sweep (zero-hit grep), tests, router discoverability,
     bongsu searchability
  8. PR workflow — separate sub-sections for external contributors
     and maintainer SMEs (mirror operating model rules cited)
  9. After-merge follow-ups — patch alpha release, eval probe,
     persona-pairing review
  10. Common pitfalls — 8-row table

### Changed
- `CONTRIBUTING.md` — added a section pointing at the new domain
  extension guide. Calls out that the 17–18 not-yet-shipped categories
  are intentionally left for domain SMEs.
- README EN/KO — added a one-line cross-reference to the new guide
  immediately after the framework-coverage inventory link.

### Why this release exists
The 0.1.0a4 inventory made the 17–18 unshipped categories visible
but didn't tell a domain SME *how* to ship one. Without a guide, the
sanitization, citation, and ship-status discipline that protects the
defensive moat would erode the moment external PRs started landing.
This release encodes the discipline.

`pip install "sillok==0.1.0a4"` and `pip install "sillok==0.1.0a5"`
are behaviorally identical at runtime.

## [0.1.0a4] — 2026-04-27

Documentation release. No code changes; READMEs and architecture
inventory only. Behaviorally identical to 0.1.0a3 at runtime.

### Added
- **`docs/architecture/framework-coverage.md`** — full inventory of
  the 25 categories / 110+ global standards Sillok's roadmap targets,
  with explicit ship status per category (today / 0.2.0a1 / 1.0.0 GA)
  and a 25-row persona pairing table (external consultant ·
  internal IC/Manager · internal Leader). The OSS-distribution
  counterpart of the upstream `00-meta/06-framework-coverage-inventory.md`.
- **README "Framework coverage" section** (EN + KO) — one-screen
  ASCII picture of the 5 axes / 25 categories with ship-status
  glyphs, the 0.1.0a3 ship table, a persona-pairing excerpt
  ("find your category fast"), and a link to the full inventory.

### Why a docs-only patch alpha
Honesty before promise: the framework coverage inventory is one of
Sillok's strongest moats, but slapping "110+ standards" onto the
README without a ship-status column would mislead 0.1.0a3 users —
only ~7 of the 25 categories actually ship today. This release adds
the inventory **with** ship status visible at every level so a
reader sees the roadmap and the alpha-reality side by side.

## [0.1.0a3] — 2026-04-27

Documentation honesty release. No code changes; READMEs and
CHANGELOG only. The 0.1.0a2 README mixed a *GA experience*
quickstart with the *alpha reality* in a way that overpromised what
currently ships — specifically the `sillok` unified command,
`sillok corpus install --starter`, and `@sillok` MCP bridge are
still alpha-stubs.

### Added
- **"Consultant Quickstart for 0.1.0a3 — what works today"**
  section in both READMEs (EN + KO). One-screen path for Biz /
  Product / Project / IT / ITO consultants:
  - point Sillok at your own RAG repository
  - select packs with `python -m sillok.naru.router_2tier`
  - search vault with `python -m sillok.bongsu.search`
  - promote new outputs with `python -m sillok.yeonryun.disposition`
  - ingest raw md with `python -m sillok.pyeonchan.ingest_md`
  - attach routed pack body to an external LLM by hand
- **Architecture-at-a-glance Mermaid section** — two views:
  - *Business view*: how a consultant gets value (vault → router →
    packs → LLM → atom promote → vault).
  - *Technical view*: 14-module data flow with a live-vs-stub
    legend (green solid = production-path in 0.1.0a3, red dashed =
    stub / Phase 1 / 0.2.0a1).
- **Gap table** — the six capabilities that are *not* yet in
  0.1.0a3, each with the milestone they land in.

### Changed
- The 60-second Quickstart at the top of each README is now
  explicitly labeled **"GA target"**. A link routes readers who
  need today's behavior to the Consultant Quickstart section.
- `pip install sillok` example version pin moved from `0.1.0a1+`
  (alpha) to `1.0.0+` (GA). The Consultant Quickstart correctly
  pins `>=0.1.0a3`.

### Why a docs-only patch alpha
Honesty over speed: 0.1.0a3 is entirely about giving readers the
right mental model for what the alpha actually does. No tests, no
API surface changes — `pip install "sillok==0.1.0a2"` and
`pip install "sillok==0.1.0a3"` are behaviorally identical at
runtime.

## [0.1.0a2] — 2026-04-26

B+ cherry-pick: the two halves of Karpathy's LLM Wiki pattern that
were missing from 0.1.0a1 — *Query* (vault search) and *Lint*
(disposition / promotion) — are now production-path. Coverage of the
upstream maintainer's daily workflow goes from ~35% to ~55%; coverage
of the external OSS scenario goes from ~80% to ~88%.

### Added
- **`sillok.bongsu.search` (B+ 1of4)** — vault-resident corpus search
  engine. `build_index()` walks a markdown vault, parses frontmatter,
  honors a `.sillok/scope-aliases.yaml` map, and excludes `.git` /
  `.obsidian` / `.sillok` / `node_modules` / `__pycache__` / `.venv`
  by default. `filter_notes()` supports scope / type / tier / status /
  topic / date_from. `fulltext_search()` uses ripgrep when available
  with a grep fallback. CLI: `python -m sillok.bongsu.search --vault
  <path> [--scope X] [--type Y] [--query "Z"] [--format
  summary|full|json] [--stats]`. 12 smoke tests.
- **`sillok.bongsu._common`** — frontmatter parser, scalar/list field
  helpers, scope alias loader, body preview extractor. Generic
  defaults — no client / pm-domain ontology baked in.
- **`sillok.yeonryun.disposition` (B+ 2of4)** — knowledge disposition
  engine. Scores reusability across 10 bilingual signal patterns
  (en + ko). Decides `none` / `local-reusable` / `cross-repo-reusable`.
  Identifies extractable atoms (max 5) by knowledge type. Generates
  vault-compatible atomic notes with frontmatter v5.4 shape. Default
  promotes only the highest-priority *representative* atom per source
  (avoids signal/noise degradation); `--extract-all` opt-in for the
  legacy fan-out path. Honors `cross_repo: false` / `disposition:
  none` opt-out keys in source frontmatter. `/tmp/` guard preserved.
  Carries `retrieval_tier` / `quality_score` from source frontmatter
  through to the result. CLI: `python -m sillok.yeonryun.disposition
  [file | --scan dir] [--auto-extract --target-dir DIR]
  [--source-repo REPO] [--topic TOPIC] [--format text|json]`. 16 smoke
  tests + 3 integration tests for the bongsu→yeonryun seam.
- **Recipes (B+ 3of4)** — `docs/recipes/search-vault-with-bongsu.md`
  and `docs/recipes/decide-reusability-with-yeonryun.md`. Recipe index
  updated.
- **Bilingual README** — `README.ko.md` Korean companion to README.md.
  Module reference table now spells out the classical meaning of each
  Korean module name (e.g. 봉수 = 烽燧 signal-fire network, 직지 = 1377
  oldest extant metal-type print).

### Changed
- `sillok.__init__` doc-comment names `sillok.yeonryun` and credits
  `sillok.bongsu` for vault search.
- `00-meta/09-coverage-vs-aipm-vault.md` §11 added — re-evaluation
  matrix vs 0.1.0a1 baseline.

### Sanitization (vs upstream `vault_search.py` / `vault-disposition.py`)
- Removed `VAULT_ROOT` defaults and `40_FullyActiveLearning` paths.
- Removed client / pm-domain ontology and AIPM-specific frontmatter
  keys.
- `source-system` changed from `aipm-research` to `sillok.yeonryun`.
- `source_repo` defaults to `$SILLOK_SOURCE_REPO` env var or `sillok`,
  no hardcoded GitHub coordinate.
- Topic defaults to `general`; honors source-frontmatter `topic:`.
- `image-template` atom-type removed (out-of-scope for OSS surface).
- English-first regex patterns; Korean kept as parallel branches so
  bilingual sources still score correctly.

## [0.1.0a1] — 2026-04-26

Functional alpha. The two step-2 items that gated the cutover are now
either landed (F0.6) or explicitly deferred (F0.3 → 0.2.0).

### Added
- **Pack bodies (F0.6 step 2)** — all 10 starter packs now ship full
  prompt bodies, not stubs. Each body is English-only, public-
  distribution form, anchored to publicly available methodologies and
  standards: PMBOK 8 / SAFe 6.0 / BABOK / SEBOK / COSO ERM 2017 / ISO
  31000:2018 / COBIT 2019 / TOGAF 10 / Three Lines Model / Porter /
  Ansoff / Blue Ocean ERRC / BMC / CRAAP / AIMQ / IQF / Bond
  Triangulation / Pyramid Principle / SCQA.
- **Empty-folder audit closeout (P0+P1+P2)** — every directory in the
  repo now has either real content or a placeholder README explaining
  its phase / activation gate. Empty directory count: 0.
- **Smoke tests** — 30 unit + 3 integration tests covering naru,
  bongsu, schemas, pyeonchan, and end-to-end route → ingest → telemetry
  flow. The remaining four module directories (jikji, sangso,
  telemetry, eval) carry namespace-import smoke tests so future PRs
  can swap in real tests without touching CI.
- **Examples** — `examples/starter-projects/{minimal, multi-pack,
  multi-tenant}/README.md` walkthroughs covering 3 archetypes.
- **Integrations** — placeholder READMEs for obsidian-vault,
  llm-wiki, claude-code, promptfoo, langfuse with phase / activation
  gate documented per integration.
- **Docs landings** — `docs/{tutorials, recipes, governance, modules,
  api, benchmarks}/index.md` populated.
- **Release script** — `scripts/release.sh` for patch / minor / major
  bumps with draft GitHub release creation.

### Deferred
- **F0.3 step 2** — cherry-pick + sanitize of `prompt_os_v2.py`
  (1235 LOC: semantic embeddings, confidence calibration, R1-R7 fixes
  for v2 routing). Defers to **0.2.0**. The 2-tier router shipped in
  0.1.0a0 remains the production path for `0.1.0a1`.

### Notes
- This is the first **functional** alpha. `pip install sillok` produces
  a working router and the 10 starter packs return substantive prompt
  bodies. Eval CI is still warn-only (flips to blocking in PR-B,
  Phase 1).
- Workshop-Retro atom type (7th type) and starter atoms (12) remain
  in the upstream `aipm/project/Harness-Sillok/04-prototypes/`
  staging area; they ship to `packs/atoms/` in 0.2.0.

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

[Unreleased]: https://github.com/sillok-os/sillok/compare/v0.1.0a1...HEAD
[0.1.0a1]: https://github.com/sillok-os/sillok/releases/tag/v0.1.0a1
[0.1.0a0]: https://github.com/sillok-os/sillok/releases/tag/v0.1.0a0
[0.0.1]: https://github.com/sillok-os/sillok/releases/tag/v0.0.1
