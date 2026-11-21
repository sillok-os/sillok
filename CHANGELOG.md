# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project
adheres to [SemVer](https://semver.org/).

## [Unreleased]

### Fixed — documentation
- Routing claims now match the code (ADR 0002): Tier 2 loads the selected
  pack bodies and routing makes no LLM call; the measured pack-instruction
  saving is about 94% (not ~97%); the 47 starter packs do not declare a
  `retrieval_plan` yet; sample outputs use the valid plan ID `vault_first`.

## [0.4.1] — 2026-11-19

**Packs Wave 3a: a new `research` category (43 → 47 packs).** Content only:
no module, CLI or router behaviour changed, so `0.4.0` → `0.4.1` upgrades
cleanly.

### Added — packs Wave 3a (research)
- `academic-paper-writing` (workflow/research) — five lenses with declared
  blind spots, contradiction map, claim reliability table, outline approved
  before prose, citations checked by identifier and for support (a title is
  not evidence), authorship and AI-disclosure gate, mock review in a fresh
  context.
- `academic-integrity-review` (workflow/research) — forensics with A/B/C
  evidence and symmetric human-authorship signals, probability verdicts only,
  no document text sent out, execution record, oral-verification protocol;
  findings-first review; proofreading that never changes meaning.
- `research-enhanced` (domain/research) — viewpoint, depth and use declared
  first; 2–6 perspectives; triangulation across method, source and
  perspective; Observed / Inferred / Recommendation labels; reflection audit
  in a fresh context.
- `deep-research` (workflow/research) — periodic seven-axis landscape scan
  of any field, cross-axis insights, drill-downs, dated events vs attributed
  forecasts, claim ledger.
- Router golden: +7 positive rows (G53–G59), including a collision row where
  `deep-research` must outrank `research-enhanced`.

## [0.4.0] — 2026-11-17

**Four kernel managers that act between messages, ported from the upstream
harness.** All of them are experimental and opt-in: nothing runs until you
install the hook; work context, playbook and recall run only when their
section is present in the kernel config; the context budget only shortens
blocks those managers produce. Each has its own off switch, and the playbook
starts in shadow mode. Their effect on answer quality has
not been measured in a controlled test. The router, the packs, the 4 gates
and the MCP bridge are unchanged, so `0.3.2` → `0.4.0` upgrades cleanly.

### Added
- **`sillok.sacho` — work context.** Holds which kind of work a session is
  doing across turns: explicit (router or profile `triggers`) > action (≥ 2
  recent writes, ≥ 70 % in one profile's path prefixes, after the last
  explicit turn) > inherited (gap ≤ 2 h, anchor ≤ 4 h). Upstream replay of 30
  days lifted work-type attribution of human turns from 31.4 % to 65.9 %.
  State is per hashed session ID, written atomically under a lock; stale
  writers cannot overwrite newer state. `SILLOK_WORK_CONTEXT=off`.
- **`sillok.seungjeongwon` — context budget.** Collapses blocks already shown
  in this session (30-min window, content hash) into pointers that keep the
  path to re-read; never grows a block; fails open; reset on compaction.
  Upstream, 22.4 % of injected context repeated within a session.
  `SILLOK_CONTEXT_BUDGET=off`.
- **`sillok.gyeongyeon` — playbook.** Lessons per work type ranked by the
  Beta mean `(h+1)/(h+x+2)`, learned from the human's next input
  (approval → helpful, correction → harmful), counted once per session ×
  item × outcome. `shadow` mode writes control counters only; `auto` shows
  ≤ 900 bytes. `promote_candidates()` lists lessons helpful in ≥ 3 sessions
  with no harm. `SILLOK_PLAYBOOK_MODE=off|shadow|auto`.
- **`sillok.chunchugwan` — memory recall.** SQLite FTS5 over memory notes
  (one chunk per heading path) and past episodes; returns ≤ 5 lines /
  900 bytes of pointers (never note bodies), with a title/heading-match gate,
  Korean particle stripping, opt-out tags, a 0.25 s refresh budget and
  best-effort redaction of secrets and contact details. Upstream recall@3
  against later opens started at 34 % — a path to measure, not a solved
  problem. `SILLOK_MEMORY_RECALL=off`.
- **`sillok.kernel.hook`** — one Claude Code `UserPromptSubmit` /
  `SessionStart(compact)` hook wiring the four managers from a JSON config.
  Synthetic example in `examples/kernel/`.
- **`sillok.eval.evidence`** — execution-evidence checker (stages, claims,
  observed basis, artifact SHA binding; batch records with a frozen ID set)
  plus its JSON contract in `sillok/eval/contracts/`.
- **`sillok.eval.request_coverage`** — Stop-hook check that every numbered
  request item (1..N) is visible in the final answer; sends the turn back
  once. `SILLOK_REQUEST_COVERAGE=off`.

### Fixed (found while porting)
- Recall hook raised `FileExistsError`/`PermissionError` when the index
  folder could not be created (only `sqlite3.Error` was caught); it now
  returns no block.

## [0.3.2] — 2026-11-17

**Packs Wave 2: 25 → 43 packs.** No API or router changes; `0.3.1` →
`0.3.2` upgrades cleanly. 18 packs were ported from the upstream harness in
four waves of at most five packs (#29–#32). The engine, the 4 gates and the
MCP bridge are the same as in `0.3.1`. The kernel managers came in `0.4.0`.

### Added — packs Wave 2d (health + travel)
- `running-injury-prevention` (domain/health) — emergency and red-flag
  routing first, four frames per injury, prevention pillars, load spikes as
  flags (ACWR caveats noted), conservative return to run.
- `running-race-data-analysis` (domain/health) — failing checkpoint first,
  slow vs stopped, same training windows, runner-owned goals.
- `nutrition` (domain/health) — eating-disorder routing, diet-pattern
  comparison with evidence tiers, no weight promises or brand doses.
- `travel-trip-planning` (domain/travel) — fixed points, identical queries,
  graded price evidence, per-stop entry rules, people pay and ticket.
- Router golden: +4 positive rows (G49–G52).

### Added — packs Wave 2c (visual production + quality)
- `design-artifact-production` — one artifact brief, claim ledger, semantic
  tokens and format adapters (image, print, slides, Word, Excel, web).
- `diagram-design` — behaviour-first type selection; one accent, 1 px
  hairlines, 4-unit grid, tokens as CSS variables, measured AA contrast.
- `visual-quality` (quality guard) — V1–V8, anti-patterns, DESIGN.md
  companion and a release gate for metadata, prompt residue and privacy.
- `image-prompt-playbook` — brief checklist, 8-slot sentence, JSON for
  multi-panel layouts, one-variable iteration, four-role A/B, safety rules.
- `gpt-image-2-reference` — low-precedence fallback to a CC BY 4.0 prompt
  catalogue with adaptation, attribution and taxonomy tags.
- Router golden: +5 positive rows (G44–G48).

### Added — packs Wave 2b (business strategy + deck builder)
- `gtm-launch-playbook` — launch tier, positioning canvas, messaging
  hierarchy, 30-60-90 plan, chasm sequencing, day-90 gate.
- `unit-economics-modeling` — exact metric formulas, segment CAC/LTV,
  cohorts, Rule of 40/X, burn multiple, mandatory 3-scenario model.
- `saas-pricing-packaging` — price metric, good-better-best tiers,
  Van Westendorp and conjoint, hybrid models, price-change playbook.
- `platform-strategy` — platform canvas, typed network effects, cold start
  with graduation condition, liquidity, take rate, platform risks.
- `deck-builder` (output style) — one request to a verified deck: action
  titles, cite-from-context, decision devices, Limits & Assumptions.
- Router golden: +5 positive rows (G39–G43).

### Added — packs Wave 2a (engineering ops + cold-domain guard)
- `sw-engineering-operations` — EARS requirements → ADR/design → RTM → red-team,
  AI-assisted development rules (D1–D9) and a delivery baseline (SD1–SD8).
- `github-operations` — choose GitHub features by repository purpose and
  observed state; staged branch protection; permission gaps stay unknown.
- `github-actions-ops` — CI execution path, honest monthly bill estimate,
  first-error-line failure triage, cost-framed human decisions.
- `cold-domain-grounding` (quality guard) — ground first in unfamiliar
  domains; codes and enums only from primary sources; mandatory
  `## Limits & Assumptions`.
- Router golden: +4 positive rows (G35–G38). Negative rows still load no pack.

## [0.3.1] — 2026-11-16

**Routing correctness + honest CI.** No API changes; `0.3.0a2` → `0.3.1`
upgrades cleanly. This is the first untagged `0.x` release: `pip install
sillok` now resolves to the real package instead of the `0.0.1`
name-reservation placeholder (pre-release tags were skipped by default).

### Fixed
- **Unmatched packs returned on precedence alone.** `tier1_match` added
  `precedence × 0.1` to every pack and kept any score above zero, so an
  unrelated message still returned the top-5 packs by precedence (5.00
  candidates per message on the router golden) and Tier 2 loaded their
  bodies. A pack is now a candidate only when an explicit trigger or a
  keyword matches; precedence only breaks ties (1.10 candidates per message).
  Observed in a real install on 2026-11-15, where a wrapper matcher had to
  work around it.
- **Abbreviations matched inside words.** Upper-case ASCII keywords such as
  `SK`, `SCR`, `PMC` matched as substrings (`SCR` in `script`). They now
  match whole tokens only, case-insensitively, and still match before a
  Korean particle (`RTM을`). Lower-case and multi-word keywords keep
  substring semantics so plurals still match.
- **Eval-delta gate crashed without a registry.** `gate_eval_delta` raised
  `FileNotFoundError` when `repo_root` had no `packs/registry.yaml`; it now
  skips like it does for an unknown pack.
- **Temp-source guard differed by platform.** `yeonryun.process_file`
  refused auto-extraction only for a literal `/tmp/` prefix, so it fired on
  Linux (pytest temp dirs live there) but not on macOS (`/var/folders`). It
  now also covers the platform temp directory, with an explicit
  `allow_temp_source=True` opt-in. Two tests had been failing on Linux.
- **CI was green while tests failed.** Every CI step ended in `|| true`, so
  three failing tests on `main` went unnoticed since 0.3.0a1. The test job
  now gates; lint and mypy stay advisory via `continue-on-error` (existing
  backlog: 36 ruff findings, 49 unformatted files) so their failures are
  visible.

### Changed
- **Router golden wired into CI** (`tests/integration/test_router_golden.py`):
  top-1 ≥ 90 %, expected pack within top-5 for every positive row, 4 new
  negative rows must load no pack, ≤ 2 candidates per message on average.
  Result on the bundled registry: top-1 30/30, top-5 30/30, negatives 4/4.
- **Trigger repairs** grounded in each pack body: `consulting-saas-audit`
  (+`SaaS`, `moat`, `Claim Verification` — its keywords were a copy of the
  PM-framework list), `exec-communication` (+`SCQA`, `MD&A`).
- **Install docs** use a `>=0.3.1` floor instead of `--pre`.

## [0.3.0a2] — 2026-08-11

**Install repair.** A fresh `pip install` could not reach a working MCP
bridge. Four independent defects compounded, and the first masked the rest,
so the visible symptom was "the MCP tools never appear" with no actionable
error. No API changes; `0.3.0a1` → `0.3.0a2` upgrades cleanly.

### Fixed
- **MCP SDK 2.0 incompatibility.** The `mcp` extra had no upper bound, so
  fresh installs resolved to SDK 2.0, which removed `mcp.server.fastmcp` —
  the module `sillok.tongsa.server` imports. `python -m sillok.tongsa serve`
  exited immediately on every new install. Pinned to `mcp>=1.2,<2`.
- **Misleading import error.** That failure was reported as "the mcp package
  is not installed", so users ran `pip install 'sillok[mcp]'`, pip reported
  the requirement already satisfied, and nothing changed. `build_server()`
  now distinguishes *missing* from *incompatible* and names the version that
  fixes it.
- **Registry unreachable outside a checkout.** The wheel shipped code but not
  `packs/`, and the registry was read from the cwd-relative
  `packs/registry.yaml`. An MCP server inherits the *host project's* working
  directory, never Sillok's, so `list_packs` / `route` / `search` raised
  `FileNotFoundError` even after the SDK pin. `packs/` is now bundled into
  the wheel as `sillok/_packs/`, and resolution follows explicit argument >
  `$SILLOK_REGISTRY` > cwd checkout > bundled — with an error that names
  every path tried. Pack bodies resolve relative to the registry that
  declared them.
- **`UnicodeEncodeError` on Windows consoles.** cp949 / cp1252 cannot encode
  the em dash and arrows the CLI prints, so the documented CLI fallback died
  too. CLI entry points re-wrap stdout/stderr as UTF-8. Only the text layer
  is touched — the MCP stdio transport wraps the raw buffer and is
  unaffected.

### Changed
- Docs corrected across `README.md`, `docs/integrations/mcp-quickstart.md`,
  `integrations/claude-code/README.md`, `mcp_server/README.md`, and
  `examples/claude-code-mcp-config.json`. They advertised the packages
  `sillok-mcp` and `sillok-tongsa` (neither published to PyPI), console
  scripts of the same names (only `sillok` is declared), a `--stdio` flag
  (the option is `--transport stdio`), and `.claude/mcp.json` /
  `settings.json` as Claude Code MCP config locations (neither is read —
  it is `.mcp.json` at the project root). Install lines now use `--pre`,
  since plain `pip install sillok` resolves to the `0.0.1` name-reservation
  placeholder, which has no submodules.

### Added
- `SILLOK_REGISTRY` environment variable — point Sillok at a registry when
  the working directory is not a checkout. Previously documented in a code
  comment but never implemented.
- `sillok.naru.router_2tier.resolve_registry` / `resolve_pack_body` /
  `bundled_registry` — public helpers for the resolution order above.
- `docs/integrations/claude-code-install-prompt.md` — a prompt that installs
  Sillok correctly from Claude Code, including a verify-before-declaring-
  success step.
- `tests/unit/test_install_contract.py` — 12 regression guards covering the
  packaging contract, registry resolution, MCP diagnostics, and console
  encoding.

## [0.3.0a1] — 2026-06-02

**Wave 2 — observability, governance evidence, and self-growth scaffolding.**
Seven new provider-neutral modules land across `telemetry` / `sangso` /
`yeonryun` / `eval` / `naru`, plus the previously-stub unified `sillok` CLI is
now functional. Additive only; `0.2.0a3` → `0.3.0a1` upgrades cleanly.

### Added
- **`sillok.telemetry.gate`** — schema-enforced telemetry write-gate: validates
  every row against `sillok.schemas.telemetry` before append so the eval /
  self-growth corpus never ingests a malformed row. Optional `divergence_hook`
  extension point. ([#17](https://github.com/sillok-os/sillok/pull/17))
- **`sillok.sangso.canary`** — shadow-vs-prod KPI canary that produces the
  evidence for the governance **Shadow** stage: record eval rounds, compare
  medians, render a markdown verdict against configurable thresholds.
  Metric-agnostic; the caller supplies metrics (e.g. `EvalSummary.to_dict()`).
  ([#18](https://github.com/sillok-os/sillok/pull/18))
- **`sillok.yeonryun.coverage`** — coverage-gap detection: cluster
  empty-selection (router-miss) messages by shared vocabulary into candidate
  trigger proposals. The gap-detection half of the auto-growth loop. Handles
  both v2-envelope and legacy telemetry shapes.
  ([#19](https://github.com/sillok-os/sillok/pull/19))
- **`sillok.eval.calibration`** — routing-confidence calibration: Brier score
  + top-pack match rate with a pass/fail verdict. Pure; pluggable `route_fn`.
  ([#20](https://github.com/sillok-os/sillok/pull/20))
- **`sillok.naru.action_layer`** — the *action* axis of 2-D routing
  (`domain × action`): classifies a message into universal action types
  (edit / explain / generate / summarize / diagram / review / plan). The
  taxonomy is domain-agnostic and overridable.
  ([#21](https://github.com/sillok-os/sillok/pull/21))
- **`sillok.yeonryun.optimizer`** — a dependency-free `Optimizer` protocol +
  reference `MutationOptimizer` for the auto-growth *improve* step.
  Proposal-only (never auto-applies); a DSPy/GEPA optimizer can implement the
  same protocol with no caller change.
  ([#22](https://github.com/sillok-os/sillok/pull/22))
- **`sillok.eval.probe_seeder`** — seed unlabelled candidate probes from a
  conversation export: redacted first-user-messages of deep conversations, with
  `expected_pack` left for human labelling. Pluggable generic-PII redaction.
  ([#23](https://github.com/sillok-os/sillok/pull/23))

### Changed
- **`sillok` unified CLI is now functional** (previously an alpha stub that
  raised `ImportError`). `sillok.cli:main` is a lazy, dependency-tolerant
  dispatcher: `sillok --version`, `sillok route "<msg>"`, and the mounted module
  groups `sillok eval` / `sangso` / `schemas` / `tongsa`. A module whose optional
  dependency is missing degrades to a clear per-subcommand error instead of
  breaking the whole command.

## [0.2.0a3] — 2026-05-13

Registry **Wave 1c** — `20 → 25 packs`. Five new meta / output-style /
health packs ship, **completing Wave 1 of the registry expansion
plan** (10 starter → 25 packs across Wave 1a/1b/1c, closing
[sillok #1](https://github.com/sillok-os/sillok/issues/1)). Additive
only; `0.2.0a2` → `0.2.0a3` upgrades cleanly.

### Added
- **`pack-maintenance`** (`packs/methodology/`) — author/maintain a
  Sillok pack via 4-Phase workflow (Rubric → TOP3 research → Draft →
  Validate) + 5-Question Quality Gate + freshness guard. Triggers:
  `[pack-maintenance]`, `[pack-author]`, `pack 작성`, `pack 보강`.
- **`prompt-sequencing-meta`** (`packs/methodology/`) — decide which
  packs to invoke in which order — 3-layer (task / lifecycle / dev)
  sequencing meta. Layer 1 5-pattern task micro-sequences; Layer 2
  6-stage PMBOK 8 lifecycle; Layer 3 D0–D3 dev sub-sequence loop.
  Triggers: `[sequence]`, `[seq]`, `[meta-sequence]`, `어느 순서로`,
  `프롬프트 시퀀싱`.
- **`agent-1on1`** (`packs/methodology/`) — coach
  `.claude/agents/<name>.md` subagent definitions via 5-Phase × GROW
  × AAR. Anthropic 4-field frontmatter audit + agentskills.io v0.9
  3-layer progressive-disclosure drill. Emits frontmatter + body
  diff patches, not rewrites. Triggers: `[agent-1on1]`,
  `[agent-coach]`, `agent 코칭`, `agent 정제`.
- **`worklog`** (`packs/output-styles/`) — Claude Code session
  telemetry → day / week / manager 3-highlight / monthly brag-doc.
  ccusage `--json` T1 source; Anthropic 8-field whitelist enforced
  (no raw prompts, no PII, no proprietary code echo). Pragmatic
  Engineer 7-category auto-labeling. Triggers: `[worklog]`,
  `[work-log]`, `[bragdoc]`, `워크로그`, `주간 보고`.
- **`everyday-health-symptom`** (`packs/methodology/`) — consumer-
  health analyst pack producing 8-section MECE 5-axis symptom
  analysis with mandatory Red-Flag routing as **first response
  line**. No diagnosis / no prescription / no dosage hard
  constraints; special-population auto-injection (pregnant /
  pediatric / geriatric / chronic). T1–T4 tiered references.
  Triggers: `[symptom]`, `[health]`, `수족냉증`, `불면`,
  `소화불량`, `요통`, `만성피로`.

### Changed
- Version `0.2.0a2` → `0.2.0a3` in `pyproject.toml` and
  `sillok/__init__.py`.
- `STATUS.md` pack count `20 → 25`; Wave 1 marked **complete**.
- README Status banner updated to `v0.2.0a3` / 25 packs.
- `scripts/check-status-drift.py` extended to also enforce
  README banner ↔ registry.yaml pack-count agreement (Wave 1b retro
  action P1).

### Compatibility
- Python 3.11+. No new required dependencies; `mcp` remains an
  optional extra. No removed APIs.
- `pip install --pre 'sillok==0.2.0a2'` → `0.2.0a3` upgraders gain
  5 new meta / output-style / health packs callable via the standard
  `naru` router or `tongsa` MCP `sillok.list_packs`. No schema change
  to the registry.

### Wave 1 retrospective (10 → 25 packs)
- Wave 1a (`0.1.0a7`): +5 packs (`meeting-minutes`,
  `change-management`, `tool-adoption-consulting`,
  `project-charter`, `infographic-design`)
- Wave 1b (`0.2.0a2`): +5 consulting Lens packs (Lens 2–5 + meta)
- Wave 1c (`0.2.0a3`, this release): +5 meta / output / health packs
- Total Wave 1 contribution: **15 new packs across 5 sub-categories**
  with 2,945 lines of upstream-anchored body content. All packs
  carry both the native Sillok schema and the additive agentskills.io
  v0.9 frontmatter.

### Validation
- `python3 -c "import sillok; print(sillok.__version__)"` →
  `0.2.0a3`
- `python scripts/check-status-drift.py` → OK on **both**
  STATUS.md and README.md banner (25 packs, three-way agreement)
- `python -m sillok.eval run` → 10/10 pass (v1 probe set unchanged;
  Wave 2 may expand probes per-pack)
- `python3 -c "import yaml,sillok.schemas as s; \
   s.RegistrySchema.model_validate(yaml.safe_load(open('packs/registry.yaml')))"` →
  passes (25 packs)

### Links
- Wave 1 umbrella issue (closing with this release): https://github.com/sillok-os/sillok/issues/1
- Wave 1b release (`0.2.0a2`): https://github.com/sillok-os/sillok/releases/tag/v0.2.0a2
- Wave 1a release (`0.1.0a7`): https://github.com/sillok-os/sillok/releases/tag/v0.1.0a7

## [0.2.0a2] — 2026-05-13

Registry **Wave 1b** — `15 → 20 packs`. Five new consulting Lens packs
ship under `packs/consulting/`, completing Lens 2–5 + meta cross-analysis
of the 6-lens consulting stack. Additive only — `0.1.0a7` → `0.2.0a2`
upgrades cleanly with no breaking changes.

### Added
- **`consulting-uxui-audit` (Lens 2)** — Nielsen 10 Heuristics
  quantitative + qualitative scoring · Friction numbering · ASCII
  wireframes · 4 redesign principles · Quick Wins Top 3. Triggers:
  `[uxui-audit]`, `[ux-audit]`, `Nielsen 10`, `UX 감사`, `사용성 감사`,
  `friction`.
- **`consulting-ai-engineering-audit` (Lens 3)** — 4-element prompt
  review (Role · Context · Task · Constraints) · Claim Verification
  5-stage pipeline · Model mix matrix · 3-layer caching · 4-axis eval
  rubric (Correctness · Faithfulness · Style · Safety). Triggers:
  `[ai-audit]`, `[prompt-audit]`, `[llm-audit]`, `RAG 감사`,
  `Claim Verification`.
- **`consulting-security-audit` (Lens 4)** — STRIDE threat model ·
  Token lifecycle audit · Least-privilege scope diff · Rate-limit +
  circuit-breaker design · GDPR/CCPA/CPRA (+ PIPA) compliance matrix ·
  5-step incident runbook. Triggers: `[security-audit]`, `[sec-audit]`,
  `STRIDE`, `GDPR`, `CCPA`, `토큰 수명주기`.
- **`consulting-growth-audit` (Lens 5)** — Event taxonomy 6-check
  audit · AARRR funnel table · NSM 3-test scoring · Aha Moment locator
  (SQL pattern) · 6-stage Retention Loop · ICE Score backlog (Top 10
  with measurable outcomes). Triggers: `[growth-audit]`, `[growth]`,
  `AARRR`, `NSM`, `Aha Moment`, `리텐션`.
- **`consulting-crossanalysis` (meta)** — Synthesize 2+ Lens audits
  into 5 cross-lens themes · axis-by-axis disagreement table +
  correction proposals · ≤ 3 Reusable Strategy Frames (Pattern +
  Decision Rule + Telemetry per frame) · composite-ranked cross-lens
  recommendations. Triggers: `[crossanalysis]`, `[cross-analysis]`,
  `[meta-audit]`, `교차분석`.
- **`STATUS.md` pack registry section** updated — current count
  `15 → 20`; Wave 1a / 1b done; Wave 1c (`0.2.0a3`) planned.
- **README status banner** updated to `v0.2.0a2` / 20 packs.

### Changed
- Version `0.1.0a7` → `0.2.0a2` in `pyproject.toml` and
  `sillok/__init__.py`.
- The Wave 1b minor-version bump (`0.1.x` → `0.2.x`) reflects the
  consulting-lens completeness milestone agreed in Issue #1.

### Compatibility
- Python 3.11+. No new required dependencies; `mcp` remains an
  optional extra. No removed APIs.
- `pip install "sillok==0.1.0a7"` → `0.2.0a2` upgraders gain 5 new
  consulting Lens packs callable via the standard `naru` router /
  `tongsa` MCP `sillok.list_packs`. No schema change to the registry.

### Validation
- `python3 -c "import sillok; print(sillok.__version__)"` →
  `0.2.0a2`
- `python -m sillok.eval run` → 10/10 pass (10-probe v1 set unchanged;
  Wave 1b-targeted probes deferred to `0.2.0a3`)
- `python scripts/check-status-drift.py` → OK (STATUS.md and
  packs/registry.yaml agree on 20 packs)
- `python3 -c "import yaml,sillok.schemas as s; \
   s.RegistrySchema.model_validate(yaml.safe_load(open('packs/registry.yaml')))"` →
  passes

### Links
- Issue #1 (Wave 1 umbrella): https://github.com/sillok-os/sillok/issues/1
- Wave 1a release (`0.1.0a7`): https://github.com/sillok-os/sillok/releases/tag/v0.1.0a7

## [0.1.0a7] — 2026-05-13

Phase F1 functional alpha. Five modules previously shipping as stubs or
absent now ship with working implementations, tests, and docs:
agentskills.io v0.9 capability discovery, 5 new packs (registry Wave
1a), `gwageo` golden probes + CI gate, `sangso` proposal-only 4-gate
pipeline, and `tongsa` MCP server bridge. Additive only — no breaking
changes; `0.1.0a6` → `0.1.0a7` upgrades cleanly.

### Added
- **`sillok.schemas.SkillsV09Frontmatter`** (#7, closes #2) —
  agentskills.io v0.9 frontmatter contract alongside Sillok's native
  pack schema. Cursor / Continue / Codex CLI / ChatGPT Desktop and
  other capability-aware MCP tools can now discover Sillok packs
  without forking the native registry contract. All 10 starter packs
  carry the additive v0.9 frontmatter; native fields untouched. New
  `python -m sillok.schemas validate-skills` CLI + 6 unit tests
  (full pack-body sweep). Design doc:
  `docs/architecture/frontmatter-compatibility.md`.
- **Registry Wave 1a — 5 new packs** (#8, refs #1, Wave 1a of 3) —
  `meeting-minutes`, `change-management`, `tool-adoption-consulting`,
  `project-charter`, `infographic-design`. Pack count 10 → 15.
  Additive only; existing 10 starter packs untouched. Waves 1b/1c
  follow in `0.2.0a2` / `0.2.0a3`.
- **`sillok.eval` v1 — `gwageo` golden probes + KPI runner** (#9,
  closes #3) — replaces 213-byte stub with a working probe runner.
  10 probes / 6 families covering all 10 starter packs. `run` (probes)
  + `triangulate` (Bond Evidence Principle #3) CLIs. `--baseline` JSON
  regression diff. v1 run: **10/10 pass, 100% citation coverage,
  p50/p95 = 0.01ms / 0.01ms**. CI gate (`.github/workflows/eval.yml`)
  replaces 3 placeholder jobs with one real `rag-probes` job (PR
  paths-filter, 30d JSON artifact retention). 9 unit tests.
- **`sillok.sangso` — proposal-only 4-gate governance** (#10,
  closes #5) — replaces 215-byte stub with working Lint / Diff /
  Eval Δ / Approval pipeline. The repo description's "proposal-only
  governance" and Top 10 Feature #4 ("hard guard against prompt
  drift and corpus poisoning") now have code matching the claim.
  `propose` / `list` / `show` / `accept` CLI. Eval gate gracefully
  skips when `sillok.eval` is not importable. Auto-merge guard
  invariant enforced by construction. 14 unit tests. Design doc:
  `docs/architecture/proposal-only-governance.md`.
- **`sillok.tongsa` — MCP server bridge** (#11, closes #4) — replaces
  absent directory with a working FastMCP bridge exposing 3 tools
  (`sillok.list_packs` / `sillok.route` / `sillok.search`). On-ramp
  for Cursor / Claude Code / Continue / Codex CLI / ChatGPT Desktop
  users — README Feature #6's single biggest differentiator now has
  an end-to-end path under 5 minutes. R1-R7 reason-code audit map on
  every `sillok.route` response. Refuses non-localhost binds. Lazy
  `mcp` import with clear `pip install sillok[mcp]` hint on miss.
  Copy-paste Cursor + Claude Code MCP configs in `examples/`. 12
  unit tests. Quickstart: `docs/integrations/mcp-quickstart.md`.

### Changed
- Version `0.1.0a6` → `0.1.0a7` in `pyproject.toml` and
  `sillok/__init__.py`.

### Compatibility
- Python 3.11+. No new required dependencies; `mcp` remains an
  optional extra. No removed APIs.
- `pip install "sillok==0.1.0a6"` users upgrading to `0.1.0a7`
  gain the 5 new modules' functionality with no required code
  changes. Existing pack registry consumers see 5 additional packs
  in `list_packs()` but no schema change.

### Validation
- `python3 -c "import sillok; print(sillok.__version__)"` →
  `0.1.0a7`
- `python -m sillok.eval run` → 10/10 pass, 100% citation coverage
- All 5 PRs landed CI-clean (mergeable / clean state at merge time)

### Links
- PR #7 — agentskills v0.9: https://github.com/sillok-os/sillok/pull/7
- PR #8 — registry Wave 1a: https://github.com/sillok-os/sillok/pull/8
- PR #9 — gwageo eval probes: https://github.com/sillok-os/sillok/pull/9
- PR #10 — sangso 4-gate: https://github.com/sillok-os/sillok/pull/10
- PR #11 — tongsa MCP: https://github.com/sillok-os/sillok/pull/11

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
