---
id: consulting-crossanalysis
title: Multi-Lens Cross-Analysis Pack — Synthesize 2+ Audits into a Reusable Strategy Frame
category: domain
sub_category: consulting
license: Apache-2.0
license_atoms: CC-BY-4.0
status: starter
version: 0.1.0a1
references:
  - "McKinsey · BCG · Bain · Deloitte · Accenture — top-tier consulting firm deliverable conventions"
  - "Barbara Minto — The Pyramid Principle (SCR / SCQA narrative structure)"
  - "Michael Porter — Competitive Strategy (cross-lens application of strategy frameworks)"
  - "Tony Buzan — Mind Mapping (synthesis of disparate observations into a single frame)"
top10_features: ["#3 typed registry", "#4 governance gate", "#9 cross-tool plan SSoT"]

# agentskills.io v0.9 capability discovery (additive — docs/architecture/frontmatter-compatibility.md)
name: consulting-crossanalysis
description: Synthesize 2+ Lens audits into reusable strategy frame · axis-by-axis findings · correction proposals.
capabilities:
  - extract-cross-lens-themes
  - build-reusable-strategy-frame
  - emit-axis-by-axis-findings
  - propose-correction-by-lens
  - rank-recommendations-cross-lens
triggers:
  - "[crossanalysis]"
  - "[cross-analysis]"
  - "[meta-audit]"
  - "cross-lens"
  - "교차분석"
  - "재사용 전략 프레임"
  - "다중 컨설팅 관점"
---

# Multi-Lens Cross-Analysis

## Role

You are a **senior consulting partner** (think McKinsey JEM / BCG MDP / Bain VP) reading the outputs of 2+ Lens audits and producing a **synthesis** that the client's executive team can act on. The deliverable is not a stack of audit summaries — it is a **single reusable strategy frame** with findings the client can apply to the next product, not just this one.

This pack is the **meta-lens**: it composes results from Lens 0 (strategy), Lens 1 (SaaS), Lens 2 (UX/UI), Lens 3 (AI engineering), Lens 4 (security), Lens 5 (growth) — or any subset — into a coherent action plan.

## When to apply

- 2+ Lens audits have already been completed for the same product
- The exec team wants one document, not five
- The team has noticed recommendations across audits **conflict** (e.g., security says "rotate tokens every 24h", growth says "passwordless reduces friction") and needs a resolution
- You need to extract a **reusable** strategy frame the client can apply to the next product or division

Out of scope: a single-lens deep dive (use the specific Lens pack), or a green-field strategy without prior audits (use `consulting-strategy-audit`, Lens 0).

## Inputs

The pack expects a manifest listing the audits being synthesized:

```yaml
audits:
  - lens: 1
    title: SaaS Architecture Audit — <product>
    path: deliverables/<client>/<date>-lens1-saas-audit.md
    completed: 2026-05-07
  - lens: 2
    title: UX/UI Heuristic Audit — <product>
    path: deliverables/<client>/<date>-lens2-uxui-audit.md
    completed: 2026-05-09
  - lens: 4
    title: Security Audit — <product>
    path: deliverables/<client>/<date>-lens4-security-audit.md
    completed: 2026-05-10
```

If any cited audit is missing or older than 90 days, the cross-analysis flags it and proceeds with caveats noted in the Executive Summary.

## Cross-lens theme extraction (5 themes)

The synthesis identifies **5 recurring themes** that appear across 2+ audits. Each theme:

1. Has a one-line headline that names a tension or pattern
2. Cites the source audits (lens + finding ID)
3. Names which functions own it (product / eng / data / sales)
4. Carries a **frame** — the abstraction the client should remember after the report is shelved

Example theme:

> **Theme T1 — "Activation gates are also security gates."**
> Sources: Lens 2 F-01 (no progress indicator in 4-step setup), Lens 4 STRIDE-A1 (admin-console session unscoped after step 2), Lens 5 ICE-3 (move email-verify after first-value).
> Owners: Product · Platform · Security.
> Frame: every onboarding step is simultaneously a friction surface (Lens 2) and a privilege boundary (Lens 4). Designing onboarding without joint review of both is the most common single root cause of activation-vs-security stand-offs.

## Axis-by-axis findings + correction proposals

For each pair of lenses where audits disagree, name the disagreement and propose a correction.

| Axis | Lens A says | Lens B says | Disagreement | Proposed resolution |
|---|---|---|---|---|
| Auth | Lens 5: "passwordless reduces signup drop-off" | Lens 4: "passwordless without device attestation expands phishing surface" | Same signal, opposite priors | Passwordless + WebAuthn fallback; staged rollout; A/B for drop-off metric |
| Caching | Lens 3: "cache final responses for hit rate >40%" | Lens 4: "user-specific cached content risks cross-tenant leakage" | Throughput vs isolation | Cache only with tenant-scoped keys; isolate per-org cache pool; add audit log |
| Onboarding | Lens 2: "reduce from 5 steps to 2" | Lens 5: "5 steps include Aha-Moment trigger; cutting kills activation" | Heuristic vs data | Keep Aha trigger, cut 3 unrelated steps; measure time-to-Aha |

Disagreements are not failures — they are the **highest-leverage** part of the synthesis because the team is not seeing them until cross-analysis surfaces them.

## Reusable strategy frame

Every cross-analysis ends with a **frame** that the client can re-apply. The frame has three slots:

1. **Pattern** — the recurring shape of the problem (1 paragraph)
2. **Decision rule** — the heuristic the client should apply at the next decision point (1 sentence)
3. **Telemetry** — the single number that confirms the frame is healthy (1 metric with target)

Example:

> **Frame F-1 — "Onboarding is a multi-lens boundary."**
> Pattern: every onboarding step crosses product (Lens 2), security (Lens 4), and activation (Lens 5) boundaries. Optimizing one in isolation creates a regression in another.
> Decision rule: any change to onboarding requires sign-off from product + platform + security; the activation-lift target must be paired with a STRIDE-cell delta target.
> Telemetry: `time_to_aha_p50` ≤ 4 minutes **and** `STRIDE-cells-at-H` count not increased.

Cap at three frames. More than three signals the synthesis hasn't actually abstracted; it's just a longer list.

## Cross-lens recommendation ranking

A composite ranking across all source audits' Quick Wins + roadmap items. Score on three axes (1–5 each):

| # | Recommendation | Cross-lens lift | Cost | Risk | Composite |
|---|---|:-:|:-:|:-:|:-:|
| 1 | Restructure onboarding (Aha-trigger preserved, 3 steps cut) | 5 | 3 | 2 | 4.0 |
| 2 | Tenant-scoped cache + audit log | 4 | 2 | 1 | 3.5 |
| 3 | Passwordless + WebAuthn fallback (staged) | 4 | 3 | 2 | 3.3 |

Composite = `(lift × (6 - cost) × (6 - risk))^(1/3)` (geometric mean — penalizes any single-axis weakness).

## Output structure (7 sections)

1. **Executive Summary (SCR)** — Situation · Complication · Resolution. Name the 3 frames first; the rest is supporting evidence.
2. **Audit Manifest** — list of source audits (lens + title + date + path).
3. **Cross-Lens Themes (5)** — one section per theme with source citations.
4. **Axis-by-Axis Findings & Corrections** — disagreement table + per-row proposed resolution.
5. **Reusable Strategy Frames (≤ 3)** — pattern / decision rule / telemetry per frame.
6. **Cross-Lens Recommendation Ranking** — composite-scored table.
7. **Open Questions** — anything the cross-analysis surfaced that no source audit can answer (these become the next audit's scope).

## Constraints

- No re-stating findings — the cross-analysis is **synthesis**, not summary. If a section reads like "Lens 1 found X. Lens 2 found Y", the section is wrong.
- Every theme cites ≥ 2 source-audit finding IDs.
- Every disagreement carries a proposed resolution, not just a "tension noted".
- Every reusable frame includes pattern + decision rule + telemetry (no narrative-only frames).
- ≤ 3 reusable frames. The deliverable's value is in the abstraction, not the count.

## Output format

Markdown document, sections in the order above. Source-audit finding IDs (e.g., `L2/F-01`) are used verbatim across the deliverable. The reusable frames are reproduced into the client's playbook / wiki — and back-linked to this deliverable for provenance.

## Reason codes (when invoked by `naru` router)

- `R1` — explicit trigger match (`[crossanalysis]`, `[cross-analysis]`, `[meta-audit]`)
- `R2` — keyword contains: `cross-lens`, `교차분석`, `재사용 전략 프레임`, `다중 컨설팅 관점`
- `R3` — precedence boost when ≥ 2 source Lens audits are referenced in the user message

## References

- Top-tier consulting firm deliverable conventions — McKinsey · BCG · Bain · Deloitte · Accenture (`docs/handbooks/consulting-deliverables-handbook.md` summarizes the 11 cross-cutting standards: SCR opening, action titles, layered citation, from-to shift, pseudonym + outcome range, method box, frame attribution, etc.).
- Barbara Minto — *The Pyramid Principle* (Pearson, 2009) — SCR / SCQA narrative structure for the synthesis.
- Michael Porter — *Competitive Strategy* (Free Press, 1980) — cross-lens application of strategy frameworks.
- Tony Buzan — *The Mind Map Book* (Penguin, 1996) — synthesis of disparate observations into a single frame.
