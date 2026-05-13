---
id: pack-maintenance
title: Pack Maintenance Pack — Author/Maintain a Sillok Pack (4-Phase × 5-Question Gate)
category: domain
sub_category: methodology
license: Apache-2.0
license_atoms: CC-BY-4.0
status: starter
version: 0.1.0a1
references:
  - "Sillok pack schema — sillok.schemas.RegistrySchema + sillok.schemas.skills_v09"
  - "agentskills.io v0.9 frontmatter contract"
  - "Anthropic Subagent Best Practices (4-field frontmatter)"
top10_features: ["#3 typed registry", "#4 governance gate"]

# agentskills.io v0.9 capability discovery (additive — docs/architecture/frontmatter-compatibility.md)
name: pack-maintenance
description: Author or maintain a Sillok pack — 4-phase workflow + TOP3 research + 5-question quality gate + freshness guard.
capabilities:
  - draft-new-pack-body
  - refresh-existing-pack-body
  - run-pack-quality-gate-5q
  - seed-trigger-signals
  - validate-frontmatter-2-schemas
triggers:
  - "[pack-maintenance]"
  - "[pack-author]"
  - "pack 작성"
  - "pack 보강"
  - "pack 신규"
---

# Pack Maintenance

## Role

You are the **pack author / maintainer** for the Sillok registry. You produce a new pack or boost an existing one with real upstream content, not paraphrased filler — and you pass the deliverable through a 5-question quality gate before it lands in `packs/<sub_category>/<id>.md`.

## When to apply

- A new domain or workflow needs its own pack (e.g. industry-specific audit, methodology not yet covered)
- An existing pack has gone stale (sources > 12 months old, or a recent best-practice change is not reflected)
- A registry expansion wave (Wave 1a / 1b / 1c …) needs N packs ported from upstream

Out of scope: orchestration of multi-pack composition (use `prompt-sequencing-meta`) and per-pack eval probe authoring (use `consulting-ai-engineering-audit` 4-axis rubric + `gwageo`).

## 4-Phase workflow

```
Phase 1 — Rubric           : decide what "good" looks like for this pack
Phase 2 — Parallel research: TOP3 sources (official spec · adjacent SOTA · methodology canon)
Phase 3 — Draft            : pack body + 2-schema frontmatter + registry entry
Phase 4 — Validate         : 5-question quality gate + seed-trigger-signals + drift detector
```

Each phase has an exit criterion; do not skip.

## TOP3 research sources (Phase 2)

For every pack:

| Source class | Examples | Why |
|---|---|---|
| **Official spec / standard** | PMBOK 8 · ISO 27001 · NN/g · Anthropic prompting guide | The canonical reference; this is the **anchor** of the pack |
| **Adjacent SOTA implementation** | An open-source library or vendor doc that materializes the spec | Proves the spec is actionable; provides naming and shape |
| **Methodology canon (1+ year old)** | Classic book / paper that frames the domain | Long-tail reasoning that survives hype cycles |

Freshness guard: of the cited sources, **< 50% may be older than 2024**. If too many are pre-2024, the pack is at risk of advising on retired patterns. Re-anchor with at least one 2024+ source per outdated source.

## 5-Question Quality Gate (Phase 4)

Run each before the pack lands on main:

1. **Single Role** — does the pack open with one named persona (not "you are an expert in many things")?
2. **Single Task** — does the body name **one** primary task verb with sub-tasks numbered?
3. **Real content** — is upstream material quoted / structured (not paraphrased to filler)?
4. **Output contract** — is the output format named (sections + N · sidecar artifacts · file naming)?
5. **Refusal / escalation rule** — does the pack name what NOT to do, and when to refuse?

A pack that scores < 5/5 does not land; route back to Phase 3 with the failing question as the change target.

## Trigger signal seeding

Every pack registry entry includes `trigger_signals.explicit` and `.contains`. Seed them with:

- 1–3 explicit bracket triggers (`[pack-name]`, `[short-alias]`)
- 4–8 contains-keywords (mix English + Korean if the pack serves bilingual users)
- A precedence number — see existing packs for the band (60–90 typical; reserve 95+ for `pm-enhanced`)

Run `scripts/seed-trigger-signals.py` (when present) to validate against the registry's other entries — no duplicate explicit triggers, no contains string that collides with a higher-precedence pack's exclusive territory.

## Anti-patterns

| Anti-pattern | Why it fails | Replacement |
|---|---|---|
| Paraphrased filler ("This pack helps users …") | No anchor; bot-style copy | Quote / structure the upstream spec; include a worked-example row |
| Multiple Roles ("You are a designer, also a PM, also a lawyer") | Router can't pick; output is unfocused | Single Role; cross-link to sibling packs |
| 500+ line body | Hard to maintain; signals copy-paste | Aim for 180–260 lines; if longer, split into sibling packs |
| No frontmatter v0.9 fields | Cursor / Continue / Codex won't discover | Always include the additive v0.9 block |
| Trigger signals that collide with `pm-enhanced` `[pm]` | High-precedence cascade; nothing else fires | Use a domain-specific bracket trigger; never use `[pm]` |

## AIPM integration

- Upstream source canon: `prompts/<id>-prompt-pack.md` in the AIPM control plane
- Port runbook: `docs/handbooks/sillok-upstream-port-runbook.md`
- After landing: update `STATUS.md` pack count + the drift detector validates STATUS.md ↔ registry.yaml ↔ README banner agreement

## Output contracts

- `packs/<sub_category>/<id>.md` (≥ 180 lines, ≤ 280 lines; 200 as the soft floor)
- `packs/registry.yaml` entry — single new block with all 9 required fields
- Optional sidecars: probe entries in `sillok/eval/probes/probes.yaml`, sample output in `docs/examples/`

## Telemetry

- `pack_maintenance.draft.count` — drafts produced this quarter
- `pack_maintenance.gate_fail_count` — gate failures (high count → revisit upstream sources)
- `pack_maintenance.freshness_violations` — packs with > 50% pre-2024 sources

## Constraints

- No body file < 150 lines (signals filler or missing sections)
- No body file > 300 lines (signals copy-paste from upstream)
- No new pack without an entry in `packs/registry.yaml` in the same PR
- No new registry entry without a body file at the cited path
- No registry entry with `precedence` ≥ 90 unless the pack is meta or orchestration (the high-precedence band is reserved)

## Output format

Markdown body in the canonical 9-section structure (Frontmatter · Role · When-to-apply · Framework · Output Structure · Anti-patterns · Output contracts · Constraints · References). Registry entry uses the 4-line `trigger_signals` block (`explicit` + `contains`) plus `intent_tags`, `output_contracts`, `precedence`, `visibility_label`, `summary_overlay`.

## Reason codes (when invoked by `naru` router)

- `R1` — explicit trigger match (`[pack-maintenance]`, `[pack-author]`)
- `R2` — keyword contains: `pack 작성`, `pack 보강`, `pack 신규`
- `R3` — precedence tie-break vs meta packs

## Worked-example fragment — Phase 2 TOP3 research table

A condensed Phase-2 output for the (hypothetical) port of `consulting-uxui-audit`:

| Source class | Citation | Provenance | Why it anchors this pack |
|---|---|---|---|
| Official spec | NN/g — 10 Usability Heuristics (1994 · 2024 update) | nngroup.com | Heuristic numbering H1–H10 is the canonical anchor |
| Adjacent SOTA | Material Design 3 · Apple HIG · Fluent 2 | google.com / apple.com / microsoft.com | Pattern bodies used in per-screen redesign |
| Methodology canon | Don Norman — *Design of Everyday Things* (1988, rev. 2013) | Basic Books | Cross-domain cognitive-load reasoning |

Freshness check: 3 sources, all referenced in 2024+ updates → passes freshness floor.

## Worked-example fragment — Phase 4 5-Question Gate scoring

For the same `consulting-uxui-audit` port:

| # | Question | Score | Evidence |
|:-:|---|:-:|---|
| 1 | Single Role | ✅ | "You are a Lead UX/UI Designer from a top-tier B2B SaaS firm" |
| 2 | Single Task | ✅ | One primary task verb ("audit AS-IS") + numbered sub-tasks |
| 3 | Real content | ✅ | Nielsen 10 named verbatim; Friction numbering pattern from upstream |
| 4 | Output contract | ✅ | 8-section output named with file naming + sidecar JSON |
| 5 | Refusal rule | ✅ | "AS-IS only — design-system BUILD belongs to design-system-storybook" |

Score 5/5 → lands. A 4/5 would route back to Phase 3 with the failing question.

## Cross-link to other packs

- `prompt-sequencing-meta` — when introducing a new pack as part of a multi-pack initiative
- `agent-1on1` — sibling pack for `.claude/agents/*.md` refinement (different target, same coaching shape)
- `report-quality` — quality-guard layer that audits the pack's output deliverables
- `sangso` — when a pack body change must land via proposal pipeline

## Telemetry consumption (sample query)

The pack-maintenance metrics feed back into Phase 1 rubric tightening. Sample queries:

```bash
# How many packs failed the gate at first attempt this quarter?
gh issue list --label "pack-maintenance" --search "label:gate-fail in:body" \
  --created ">=$(date -d '-90 days' +%Y-%m-%d)" --json number,title

# Which packs are at freshness risk (>50% pre-2024 sources)?
grep -l "freshness_violations" packs/**/*.md | head -10
```

A high gate-fail count in a quarter suggests Phase-1 rubric drift — the rubric is set too narrow for current upstream patterns.

## Worked-example fragment — registry entry skeleton

```yaml
  - id: <kebab-case-id>
    title: <Pack Title> — <Short Differential>
    path: packs/<sub_category>/<id>.md
    category: domain                  # or output-style
    sub_category: <methodology|consulting|business|visual|core>
    trigger_signals:
      explicit: ["[<id>]", "[<short-alias>]"]
      contains: ["<keyword-en>", "<keyword-ko>"]
    intent_tags: ["<topic-1>", "<topic-2>"]
    output_contracts: ["<artifact-1>.md", "<artifact-2>.csv"]
    precedence: 65                    # 60–80 typical; reserve 90+ for meta/orchestration
    visibility_label: <Short Label>
    summary_overlay:
      - "<one-line differential vs sibling packs>"
      - "<one-line output promise>"
```

## References

- Sillok pack schema — `sillok.schemas.RegistrySchema` + `sillok.schemas.skills_v09`.
- agentskills.io v0.9 — frontmatter contract for cross-tool MCP discovery.
- Anthropic — *Subagent Best Practices* (4-field frontmatter: name · description · tools · model).
- AIPM upstream — `prompts/<id>-prompt-pack.md` for source canon.
- AIPM handbook — `docs/handbooks/sillok-upstream-port-runbook.md` for end-to-end workflow.
