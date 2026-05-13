# Sillok Eval — Golden Probe Set v1

> **Status**: shipped in v0.2.0a1 · Issue [#3](https://github.com/sillok-os/sillok/issues/3)
> **Probes**: `sillok/eval/probes/probes.yaml` (10 probes, 6 families)
> **Runner**: `python -m sillok.eval run`

## What it tests

Each probe asserts that `naru.router_2tier.tier1_match` selects the **expected pack** for a given natural-language query. This guards against:

- **Routing miss** — query enters but no pack scored
- **Routing drift** — refactor accidentally re-ranks a pack out of top-K
- **Pack drift** — a pack's `trigger_signals` regress so previously-routable queries no longer match

It deliberately does **not** test pack body content — that is a separate concern (see `docs/architecture/proposal-only-governance.md` for the 4-gate flow).

## Probe families (v1)

| Family | Probes | Expected packs |
|---|:---:|---|
| `pm-lifecycle` | 3 | pm-enhanced, itil-operations |
| `methodology` | 2 | risk-uncertainty, safe-agile-delivery |
| `governance` | 2 | governance-standards, portfolio-governance |
| `consulting` | 1 | consulting-strategy-audit |
| `output-style` | 1 | exec-communication |
| `quality-guard` | 1 | report-quality |

10 probes covering all 10 starter packs ships v1. v2 (≥17 probes) lands when Wave 1b/1c packs arrive.

## KPI gates

Defined in `probes.yaml` under `kpi_targets`:

| KPI | Target | Source |
|---|---|---|
| `retrieval_p50_ms` | ≤ 100 | Whole-set Tier-1 keyword-match latency |
| `citation_coverage_pct` | 100 | Every probe produces ≥1 candidate |
| `token_reduction_pct` | 30 | vs naive load-all-packs (computed at runtime when LLM execution is wired) |

The runner emits all four KPIs in JSON via `--json` and as a human report otherwise.

## Running

```bash
# Full run
python -m sillok.eval run

# Single family
python -m sillok.eval run --family pm-lifecycle

# JSON for CI / baseline diff
python -m sillok.eval run --json > .sillok/eval-$(date +%Y%m%d).json

# Diff vs baseline
python -m sillok.eval run --baseline tests/fixtures/baseline-2026-05.json
```

Exits non-zero if any probe fails — suitable as a pre-merge gate.

## Bond Evidence triangulation gate

Independent of probes: `sillok.eval.triangulation` scores markdown reports against Bond Evidence Principle #3 (≥3 sources per claim). This is a **lightweight** heuristic port — for high-evidence audiences (board, regulator), use a parser-grade tool.

```bash
# Lenient (default) — report only
python -m sillok.eval triangulate path/to/report.md

# Strict — exit 1 on failure (CI gate for board-audience reports)
python -m sillok.eval triangulate path/to/report.md --strict

# Custom threshold
python -m sillok.eval triangulate path/to/report.md --min-sources 5 --strict
```

Scored sections (heuristic): `## Executive Summary`, `## Key Findings`, `## Findings`, `## Highlights`, `## Top Insights`, plus Korean equivalents (`## 개요`, `## 핵심 요약`).

Source signals counted within ±5 lines of each claim:
- Markdown links `[text](url)`
- Footnote refs `[^1]`
- Inline `Source:` / `출처:` annotations

## Evolution

- **v1** (this release) — 10 probes / 6 families; all 10 starter packs covered
- **v2** (Wave 1b lands) — 17+ probes / 8 families; new consulting Lens packs covered
- **v3** (LLM execution wired) — token-reduction KPI computable; cross-validation against actual answer quality

## Why these probes (selection criteria)

1. **One probe per pack minimum** — every shipped pack has at least one probe targeting it
2. **Natural-language phrasings, not just trigger tokens** — exercises both `explicit` and `contains` matchers
3. **Mix of `require_top1` (strict) and `top_k=3` (lenient)** — strict for unambiguous queries, lenient for queries that legitimately span packs
4. **Citation coverage is hard 100%** — a query with 0 candidates is always a router bug
