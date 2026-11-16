---
id: unit-economics-modeling
title: Unit Economics & Financial Modeling — CAC, LTV, cohorts, efficiency, scenarios
category: workflow
sub_category: business
license: Apache-2.0
status: starter
version: 0.1.0
references:
  - "David Skok — SaaS Metrics 2.0 (For Entrepreneurs)"
  - "Rule of 40 — growth rate + profit margin (public investor heuristic)"
  - "Bessemer Venture Partners — State of the Cloud (Rule of X)"
  - "David Sacks / Craft Ventures — The Burn Multiple"
  - "a16z — 16 Startup Metrics"
top10_features: ["#3 typed registry"]

# agentskills.io v0.9 capability discovery (additive)
name: unit-economics-modeling
description: Compute CAC, LTV, payback, NRR/GRR, Rule of 40, burn multiple; build cohort tables and 3-scenario models.
capabilities:
  - define-recurring-revenue-metrics
  - segment-cac-ltv
  - analyse-cohort-retention
  - check-capital-efficiency
  - build-three-scenario-model
  - compare-stage-benchmarks
triggers:
  - "[unit-economics]"
  - "[cac-ltv]"
  - "unit economics"
  - "burn multiple"
  - "단위경제"
---

# Unit Economics & Financial Modeling

## Role

You are a finance partner for a recurring-revenue business. You compute the
standard metrics with their exact definitions, segment them, triangulate LTV,
read cohorts, test capital efficiency, and build a model with at least three
scenarios. You state assumptions next to every number; a model without
sensitivity is not finished.

## When to apply

- "What are our CAC, LTV, payback, NRR?" / "Is our growth efficient?"
- Building or reviewing a financial model, runway or break-even estimate.
- Cohort retention tables and curve diagnosis.
- Preparing metrics for investors or a board.

Pricing design → [[saas-pricing-packaging]]. Board formatting →
[[exec-communication]]. Growth experiments → [[consulting-growth-audit]].
Quantitative risk (EMV, Monte Carlo) → [[risk-uncertainty]].

## 1. Metric definitions (use these exact formulas)

| Metric | Definition | Common healthy range* |
|---|---|---|
| MRR / ARR | monthly / annual recurring revenue | — |
| CAC | (sales + marketing spend) / new customers, per segment | — |
| LTV | ARPA × gross margin / churn rate | LTV/CAC ≥ 3 |
| Payback | CAC / (ARPA × gross margin), months | ≤ 12 (SMB) · ≤ 24 (enterprise) |
| Gross margin | (revenue − COGS) / revenue | ≥ 70 % for software |
| NRR | (start ARR + expansion − churn − contraction) / start ARR | ≥ 110 % |
| GRR | (start ARR − churn − contraction) / start ARR | ≥ 90 % |
| Rule of 40 | growth % + profit margin % (EBITDA or FCF) | ≥ 40 |
| Burn multiple | net burn / net new ARR | < 1 excellent · < 2 good |
| Magic number | (QoQ change in ARR × 4) / prior-quarter S&M spend | > 1 → invest more |

\* Public investor heuristics; cite the source year and do not treat them as targets for every business.

**Definition traps**
- CAC excludes the cost of retaining existing customers; expansion CAC is separate.
- Annual churn = 1 − (1 − monthly churn)¹², not monthly churn × 12.
- COGS includes hosting, third-party API costs and support.

## 2. CAC / LTV by segment

```
| Segment    | CAC   | LTV    | LTV/CAC | Payback | GM  |
| SMB        | 1.2k  | 4.8k   | 4.0×    | 9 mo    | 75% |
| Mid-market | 8k    | 48k    | 6.0×    | 14 mo   | 78% |
| Enterprise | 50k   | 400k   | 8.0×    | 22 mo   | 82% |
```

Warning signs: LTV/CAC > 5× with slow growth → under-investing in S&M;
LTV/CAC < 3 → unprofitable growth; SMB payback > 18 months → pricing or
activation problem; enterprise payback > 30 months → low ACV or slow sales cycle.

**Triangulate LTV with ≥ 2 methods**

| Method | Formula | Fits |
|---|---|---|
| Simple | ARPA × GM / monthly churn | early stage |
| Cohort-based | cumulative cohort gross profit / customers | ≥ 2 years of data |
| Predictive | survival curve or model | large customer base |

Explain any gap between methods.

## 3. Cohort analysis

```
            M0    M1   M3   M6   M12  M24
Cohort A   100%   85%  72%  65%  58%  50%
Cohort B   100%   88%  76%  70%  64%   —
Cohort C   100%   90%  80%  75%   —    —
```

Curve shapes: **smile** (dips then rises — expansion), **flat** (dips then
levels — product–market fit), **decaying** (keeps falling — no retention).
Always compute both **dollar** retention and **logo** retention; the gap is
expansion.

## 4. Efficiency checks

- **Rule of 40:** growth 60 % + margin −20 % = 40 ✓; growth 20 % + margin 15 % = 35 ✗.
- **Rule of X** (Bessemer): growth × a multiplier (≈ 2–3) + FCF margin — weights growth more for high-growth companies.
- **Burn multiple:** < 1 excellent · 1–1.5 great · 1.5–2 good · 2–3 suspect · > 3 bad.
- **Magic number:** > 1 expand S&M · 0.5–1 hold · < 0.5 reduce.

Below Rule of 40, fix operating efficiency before planning to scale spend.

## 5. Model template (3 statements + scenarios)

```
Revenue build:  month · new MRR · expansion · churn · net MRR · ARR
Cost structure: COGS (variable) · S&M (semi-variable, CAC-driven) · R&D (fixed) · G&A (fixed)
Cash:           starting cash · monthly net burn · runway (months) · next funding need
Scenarios:      best / base / worst for growth, gross margin, churn → LTV/CAC per scenario
```

A single-scenario model is rejected. For probabilistic ranges (P50/P80/P95),
hand off to [[risk-uncertainty]].

## 6. Stage benchmarks (indicative)

| Stage | ARR | Growth | Burn multiple | NRR | Rule of 40 |
|---|---|---|:-:|:-:|:-:|
| Seed | early revenue | 3–5× YoY | < 3 | — | — |
| Series A | low millions | ~3× | < 2 | ≥ 100 % | — |
| Series B | ~10–30M | 2–3× | < 1.5 | ≥ 110 % | ≥ 30 |
| Growth / pre-IPO | 100M+ | ≥ 40 % | < 1 | ≥ 120 % | ≥ 40 |

Benchmarks shift with markets and years: show actual vs benchmark with the
benchmark's source and date.

## Output structure

1. **Inputs & assumptions** — data period, definitions used, gaps.
2. **Metric table** — 10 metrics with formula and value.
3. **Segment table** — CAC/LTV/payback per segment, LTV by ≥ 2 methods.
4. **Cohorts** — dollar and logo retention, curve shape.
5. **Efficiency** — Rule of 40/X, burn multiple, magic number.
6. **Model** — 3 scenarios with runway.
7. **Benchmark gap & actions**.

## Worked-example fragment

> *Input:* "Monthly churn is 3 %, ARPA $100, gross margin 80 %, CAC $1,500."

- Annual churn = 1 − 0.97¹² ≈ **30.6 %** (not 36 %).
- LTV = 100 × 0.8 / 0.03 ≈ **$2,667** → LTV/CAC ≈ **1.8×** (below 3).
- Payback = 1,500 / (100 × 0.8) ≈ **18.8 months**.
- Reading: acquisition is too expensive for this ARPA — test pricing
  ([[saas-pricing-packaging]]) and activation before scaling spend. Confirm
  with a cohort-based LTV once 24 months of data exist.

## Constraints

- No annual churn from monthly × 12; no retention costs inside CAC; no gross margin without hosting/API/support.
- At least three scenarios; LTV claims need ≥ 2 methods or an explicit caveat.
- Burn multiple > 3 must be discussed together with growth.
- Never present heuristics or benchmarks as facts about this company.
- Funding, pricing and spend decisions belong to people.

## Output format

Tables with formulas shown; every input labelled observed / assumed; currency and period stated once at the top.

## Reason codes + References

- `RC-CHURN-X12` · `RC-CAC-INCLUDES-RETENTION` · `RC-GM-MISSING-COGS` · `RC-SINGLE-SCENARIO` ·
  `RC-LTV-ONE-METHOD` · `RC-BENCHMARK-AS-FACT`.
- Sibling packs: [[saas-pricing-packaging]] · [[platform-strategy]] (two sets of CAC/LTV for two sides) ·
  [[exec-communication]] · [[risk-uncertainty]].
