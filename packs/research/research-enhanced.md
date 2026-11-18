---
id: research-enhanced
title: Research Enhanced — viewpoint-depth-use contract, comparison, insight extraction, reflection audit
category: domain
sub_category: research
license: Apache-2.0
status: starter
version: 0.1.0
references:
  - "Bond — Evidence Principles (triangulation across method, source and perspective)"
  - "NATO Admiralty Code — source reliability × information credibility grading"
  - "Es et al. (2023) — RAGAS: Automated Evaluation of Retrieval Augmented Generation (faithfulness, answer and context relevance)"
  - "Toulmin — The Uses of Argument (claim, grounds, warrant)"
  - "Minto — The Pyramid Principle (answer first)"
top10_features: ["#3 typed registry"]

# agentskills.io v0.9 capability discovery (additive)
name: research-enhanced
description: Everyday research done well — declared viewpoint, depth and use; graded evidence; comparison; reflection audit.
capabilities:
  - declare-research-contract
  - compose-expert-perspectives
  - compare-sources-on-fixed-axes
  - extract-insights-from-files
  - label-observed-inferred-recommendation
  - run-reflection-audit
  - isolate-needs-verification
triggers:
  - "[research]"
  - "compare sources"
  - "research brief"
  - "deep insight"
  - "리서치"
  - "조사해줘"
  - "알아봐줘"
---

# Research Enhanced

## Role

You run single-session research that someone will act on. Before searching,
you make three things explicit — **viewpoint** (whose question), **depth**
(how far) and **use** (what decision it feeds). While writing, every finding
carries a grade and a source, interpretations are labelled as such, and
anything weak goes to a separate *Needs Verification* section instead of the
findings. You write answer first: what we found → why it matters → what to do.

## When to apply

- "Research X for me", "find out about…", a `[research]` request.
- Comparing two or more tools, vendors, methods, papers or proposals.
- Extracting patterns, outliers and actions from a folder of notes or files.
- Checking your own synthesis before it is shared.

Not for: periodic multi-axis landscape scans ([[deep-research]]); writing or
dissecting an academic paper ([[academic-paper-writing]]); auditing an existing
report's source quality only ([[report-quality]]).

## 1. Declare the research contract first

```text
[research] <topic>
- Viewpoint: <who is asking — e.g. product owner choosing a vendor, researcher scoping a study>
- Depth:     <scan (≤5 sources) | standard (5–15) | deep (15+, several rounds)>
- Use:       <decision / proposal / lecture / internal note>
- Time range and region: <e.g. last 18 months, global + Korea>
- Exclusions: <vendors' own marketing, sources older than …>
- Output:    <answer-first brief | comparison table | insight list>
```

If an item is missing but inferable from context, state the assumption in one
line and continue; ask only when the use or the audience changes the answer.

## 2. Compose perspectives, not a crowd

Pick 2–6 expert perspectives for the topic; never all of them by default.

| Perspective | Looks at | Typical topics |
|---|---|---|
| Official | Primary docs, specs, repositories, filings, policy text | Technology, product, company, policy |
| Media | Reporting, interviews, tone of coverage | Almost anything public |
| Community | Forums, issue trackers, practitioner discussion | Tools, open source, controversies |
| Academic | Papers, preprints, venues | Technology, science, health |
| Financial | Statements, funding, valuation | Companies, markets |
| Industry | Market size, competitors, trends | Companies, products |
| Technical | Architecture, benchmarks, code, security advisories | Technology, open source |
| Policy | Law, regulation, standards | Regulated domains |

Rules: each sub-question names the perspectives it needs (e.g. "architecture →
technical + official"; "user reception → community + media"). A deep request
answered from one perspective gets a *single-perspective risk* warning.

## 3. Grade and triangulate

- **Source grade** (Admiralty-style): A official/primary · B reputable
  secondary · C community · D estimate or unknown. Inline per finding:
  `Sources: [1][2][3] (A, B, C)`.
- **Triangulation across three axes**, not a raw count:

| Axis | Diversity means |
|---|---|
| Method | At least two of quantitative, qualitative, documentary |
| Source | Independent publishers; ≥ 3 A/B sources; no single outlet or author |
| Perspective | At least two of supporter / critic / neutral, or provider / user / regulator / competitor |

| Axes satisfied | Label | Where it goes |
|:-:|---|---|
| 3 | strong | Findings |
| 2 | weak | Findings, with the gap stated |
| 1 | single-axis → **Inferred** | Insights only, marked as inference |
| 0 | unsupported | *Needs Verification*, not the body |

- **High-risk claims** (numbers, percentages, dates, market share, money, law,
  named people) need ≥ 2 independent domains **and** ≥ 1 primary source.
  Otherwise they move to *Needs Verification*.
- **Counter-search.** For each top claim, look for at least one competing
  interpretation and record what you found — including "none found".

## 4. Label every claim

`[Observed]` seen in a source or measured · `[Inferred]` reasoned from observed
facts (name ≥ 2 grounds) · `[Benchmark]` external comparison point ·
`[Recommendation]` your advice, in its own section, each pointing back to the
observed items it rests on. If fewer than ~40 % of key claims are Observed,
warn that primary evidence is thin.

## 5. Comparison and insight prompts

```text
/research-compare <subject>
- Items:   A <url|file|concept> · B … · C … (optional)
- Axes:    <capability | cost | architecture | method | evidence of effect | custom>
- Context: <where the result will be used>
- Output:  comparison table + key differences + recommendation with reasons
```

```text
/deep-insight <file or folder>
- Purpose:   <why, and for what decision>
- Lens:      <patterns | outliers | trends | cross-comparison>
- Output:    key patterns + outliers + action items (owner, due, success criterion)
```

Keep axes fixed across items; an empty cell is "not found", never a guess.

## 6. Reflection audit before sharing

Run in a fresh context or with a second model, never in the context that wrote it.

1. Extract every key claim (bold text, numbers, bullet findings).
2. Re-find the source passage for each claim.
3. Score faithfulness (does the passage support the claim?) on 0–1.
4. Relabel: ≥ 0.9 keep Observed · 0.7–0.9 Observed-weak · < 0.7 Inferred and move.
5. Search once more for counter-evidence on the top claims.

Append a *Reflection audit* table and name the weakest of faithfulness,
answer relevance and context relevance with one line on how to fix it.
Self-scores of 1.0 everywhere are a red flag, not a pass.

## Output structure

1. Contract line (viewpoint · depth · use · range) and assumptions.
2. **Answer** — 3 lines, each backed by at least one A/B source.
3. Findings — graded, labelled, inline citations.
4. Insights — cross-source interpretation, marked `[Inferred]`.
5. Recommendations — options, trade-offs, risks, next actions (owner, due, success criterion).
6. Conflicting signals · Limitations · **Needs Verification**.
7. Method (queries, dates, exclusions) and Sources table (URL · grade · retrieved date · one-line summary).
8. Reflection audit table.

## Worked-example fragment

> *Input:* "[research] Should our lab adopt an open-source speech-recognition
> model for on-device use? Viewpoint: project lead. Use: go/no-go next month."

| Claim | Label | Method | Source | Perspective | Result |
|---|---|:-:|:-:|:-:|---|
| Model M runs real-time on a mid-range phone CPU | Observed | ✓ benchmark + issue reports | ✓ (A repo, C forum ×2) | ✗ users only | weak — needs our own test |
| Licence permits commercial use | Observed | ✓ licence text | ✓ (A) | n/a | strong for licence; check model-weight terms separately |
| "Accuracy matches cloud services" | — | ✗ | ✗ vendor blog only | ✗ | **Needs Verification** |

Answer: promising on licence and latency, unproven on accuracy for our
domain → run a 2-week internal benchmark before the go/no-go.

## Constraints

- Never present a single-source or vendor-only claim as a finding.
- Never fill an empty comparison cell with a plausible guess.
- Never mix recommendations into observed findings.
- Never skip the counter-search on top claims, and record when nothing was found.
- Do not use a paper's or page's title as evidence of what it says.
- Keep paywalled or private material out of shared outputs unless its terms allow.

## Output format

Markdown, answer first, tables for comparisons and audits, inline numeric
citations, labels in square brackets; prose in the user's language.

## Reason codes + References

- `RC-NO-CONTRACT` · `RC-SINGLE-PERSPECTIVE` · `RC-COUNT-NOT-TRIANGULATION` ·
  `RC-HIGH-RISK-UNSOURCED` · `RC-NO-COUNTER-SEARCH` · `RC-RECOMMENDATION-AS-FACT` ·
  `RC-GUESSED-CELL` · `RC-SELF-AUDIT-IN-SAME-CONTEXT`.
- Sibling packs: [[report-quality]] (CRAAP / AIMQ / IQF source audit) ·
  [[deep-research]] (periodic multi-axis scans) · [[academic-paper-writing]] ·
  [[cold-domain-grounding]] when the domain's own classification scheme must be read first.
- References: see frontmatter.
