---
id: deep-research
title: Deep Research — periodic multi-axis landscape synthesis with drill-downs and an evidence gate
category: workflow
sub_category: research
license: Apache-2.0
status: starter
version: 0.1.0
references:
  - "Bond — Evidence Principles (triangulation across source, method, perspective)"
  - "CRAAP Test — currency, relevance, authority, accuracy, purpose"
  - "Minto — The Pyramid Principle (answer first, MECE issue tree)"
  - "Deep-research engines (e.g. ChatGPT Deep Research, Gemini Deep Research) — vendor documentation"
top10_features: ["#3 typed registry"]

# agentskills.io v0.9 capability discovery (additive)
name: deep-research
description: Periodic multi-axis landscape scan of a field — people to role impact — with dated events and a claim ledger.
capabilities:
  - fix-period-and-field
  - scan-seven-axes
  - derive-cross-axis-insights
  - drill-down-person-organisation-crosscut
  - track-dated-events
  - separate-events-from-forecasts
  - keep-claim-ledger
triggers:
  - "[deep-research]"
  - "deep research"
  - "landscape scan"
  - "trend synthesis"
  - "심층 리서치"
  - "동향 분석"
---

# Deep Research

## Role

You run a **periodic landscape scan** of one field — monthly or quarterly —
across seven axes, then cross the axes to find what no single axis shows. You
write prompts that deep-research engines can execute, or execute them yourself
with retrieval. Subjects are not hard-coded: the engine selects the most
influential people, organisations and technologies **for that period**. Events
carry dates and sources; forecasts are kept apart from what happened. Drill
down only where the scan says it matters.

## When to apply

- "What happened in <field> this month / quarter?", trend or landscape reviews.
- Preparing a periodic briefing, a curriculum refresh, a strategy offsite input.
- A deep profile of one person, one organisation, or one cross-cutting theme.

Not for: a single question that needs good sources ([[research-enhanced]]);
paper reading or writing ([[academic-paper-writing]]); auditing an existing
report ([[report-quality]]).

## 1. Fix the frame before the scan

| Parameter | Example |
|---|---|
| Field | "on-device AI", "battery materials", "public-sector cloud" |
| Period | `2026-10-01 ~ 2026-10-31` (monthly) or `2026 Q3` (quarterly) |
| Region | global · plus one market of interest |
| Reader's role | e.g. research lead, product owner, project manager |
| Output use | briefing, curriculum update, portfolio review |

The period is fixed; nothing outside it counts as "new". The reader's role
drives axis 7.

## 2. The seven axes (soft-coded)

| # | Axis | Selection rule for the period | Must include |
|:-:|---|---|---|
| 1 | People | Top 10 most influential in the field | Role, key statement (original + translation + context), why it matters |
| 2 | Organisations | Top 10 driving the field | Strategy, monetisation, ecosystem moves, regulatory exposure |
| 3 | Application domains | Top 5 where adoption moves fastest | Adoption evidence, blockers |
| 4 | Solutions / platforms | Top 10 drawing attention | What changed this period, who uses it |
| 5 | Technologies | Top 5 advancing fastest | Maturity signal (paper → prototype → product) |
| 6 | Business models | Monetisation types and go-to-market shifts | Pricing or packaging changes with dates |
| 7 | Role impact | How the field changes the reader's role | Tasks replaced or augmented, new skills, concrete cases, topics for training |

**Cross-axis insights (Top 5).** Each links ≥ 3 axes, e.g. "person A's
organisation B applies technology C through solution D in domain E → meaning
for the reader's role". An insight that touches one axis is a finding, not an insight.

## 3. Engine prompt — monthly scan

```text
[Deep Research Request — <field> seven-axis monthly scan]
Period: <YYYY-MM-01> ~ <YYYY-MM-DD>. Region: <global + X>. Reader: <role>.
Do not hard-code subjects; select the most influential ones for this period.
Axes 1–7 as defined: people (Top 10), organisations (Top 10), domains (Top 5),
solutions (Top 10), technologies (Top 5), business models, impact on <role>.
Then: 5 cross-axis insights, each linking at least three axes.
Rules: every fact has an inline source URL and a date; quotes keep original
wording, translation and context; forecasts go in a separate "Outlook" section;
anything single-sourced is marked [unverified].
Output: Markdown, one H2 per axis, people and organisations as tables,
cross-axis insights section, event timeline table, references at the end.
```

Quarterly variant: same frame over the quarter, plus **changes in competitive
structure, adoption maturity and commercial outlook**, and a list of topics to
add to or drop from training material.

## 4. Drill-down prompts (only when the scan points there)

- **A — Person profile:** background, decisions in the period, statements
  (original + translation + context), influence on organisations and policy,
  consistency between statements and actions.
- **B — Organisation profile:** strategy, products, monetisation, partnerships,
  ecosystem, regulatory issues, dated event log for the period.
- **C — Cross-cut:** C-1 field-wide quarterly review (top trends, release
  timeline, competitive shifts, regulation by region, role implications);
  C-2 cross-analysis of 5 leaders' decisions and their knock-on effects.

| Situation | Use |
|---|---|
| "Show me the whole field this month" | §3 monthly scan |
| "Quarterly review" | §3 quarterly variant |
| "Go deep on this person / company" | A / B |
| "How do these leaders' moves interact?" | C-2 |

## 5. Evidence gate and claim ledger

- No unsupported fact becomes a finding or recommendation.
- Every executive-level claim has a row:

| Claim | Source(s) | Date | Confidence | Limitation | Use |
|---|---|---|---|---|---|

- **Triangulate priority claims** across at least two of source, method and
  perspective; single-source claims are hypotheses.
- **Tier sources:** primary/official · analyst or consulting · news · blog or
  community · user-provided. Prefer the newest primary source inside the period.
- **Events vs forecasts:** an event has a date and a source; a forecast names
  who forecasts it. Never upgrade a forecast to an event.
- **Counter-evidence:** for each of the top insights, record one competing
  interpretation and what was found.
- **Needs Verification** collects stale, single-source and contradictory items.

## Output structure

1. Frame line (field · period · region · reader).
2. Executive answer — what changed, why it matters to the reader, what to do.
3. Axes 1–7 (tables for people, organisations, solutions).
4. Cross-axis insights (5).
5. Dated event timeline · Outlook (forecasts, attributed).
6. Claim ledger · Needs Verification · Limitations.
7. References with retrieval dates.

## Worked-example fragment

> *Input:* "[deep-research] on-device AI, 2026 Q3, reader = project lead at
> a hardware start-up."

| Date | Event | Axis | Source tier | Note |
|---|---|:-:|---|---|
| 2026-07-xx | Vendor V ships a 3B-parameter model runtime for phones | 4, 5 | primary (release notes) | event |
| 2026-08-xx | Analyst firm F forecasts on-device share of inference | 6 | analyst | **Outlook**, attributed to F |

Cross-axis insight (axes 2 · 5 · 7): runtime vendors now ship evaluation
harnesses with the runtime → PM plans should budget an on-device evaluation
gate per release, not one at the end. Confidence: medium (two primary sources,
one perspective) → counter-search noted in the ledger.

## Constraints

- Never hard-code the "top" subjects before the period is scanned.
- Never count an event outside the fixed period as new.
- Never present a forecast as an event, or a vendor claim as an independent finding.
- Never translate a quote without keeping the original and its context.
- Results are a briefing, not a knowledge base: promote items to long-term notes only after a human selects them.

## Output format

Markdown, answer first, one H2 per axis, tables for people, organisations,
events and the claim ledger; inline URLs with dates; prose in the reader's language.

## Reason codes + References

- `RC-PERIOD-DRIFT` · `RC-HARDCODED-SUBJECTS` · `RC-FORECAST-AS-EVENT` ·
  `RC-SINGLE-AXIS-INSIGHT` · `RC-QUOTE-WITHOUT-ORIGINAL` · `RC-UNSOURCED-CLAIM` ·
  `RC-NO-COUNTER-EVIDENCE`.
- Sibling packs: [[research-enhanced]] for single questions · [[report-quality]] ·
  [[exec-communication]] for turning the briefing into an executive memo.
- References: see frontmatter.
