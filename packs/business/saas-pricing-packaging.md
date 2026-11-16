---
id: saas-pricing-packaging
title: SaaS Pricing & Packaging — price metric, tiers, willingness to pay, price changes
category: workflow
sub_category: business
license: Apache-2.0
status: starter
version: 0.1.0
references:
  - "Madhavan Ramanujam & Georg Tacke — Monetizing Innovation"
  - "Peter van Westendorp — Price Sensitivity Meter (1976)"
  - "OpenView — SaaS pricing and usage-based pricing reports"
  - "Simon-Kucher — pricing strategy publications"
top10_features: ["#3 typed registry"]

# agentskills.io v0.9 capability discovery (additive)
name: saas-pricing-packaging
description: Design software pricing — choose the price metric, build good-better-best tiers, estimate WTP, plan price changes.
capabilities:
  - choose-price-metric
  - design-good-better-best-tiers
  - run-van-westendorp-analysis
  - estimate-willingness-to-pay
  - design-hybrid-pricing
  - plan-price-change
triggers:
  - "[pricing]"
  - "[packaging]"
  - "willingness to pay"
  - "Van Westendorp"
  - "가격 정책"
---

# SaaS Pricing & Packaging

## Role

You design how a software product charges: the unit you charge for, how
features are packaged into tiers, what customers are willing to pay, and how
to change prices without breaking trust. You design; benchmarking an existing
price list is an audit ([[consulting-saas-audit]]), and LTV/CAC consequences
are modelled in [[unit-economics-modeling]].

## When to apply

- Setting prices for a new product or plan; adding a free tier or trial.
- Choosing per-seat vs usage vs outcome pricing.
- Designing or simplifying plans and tiers.
- Running a pricing survey or estimating willingness to pay.
- Raising prices or changing the price metric.

Marketplace take rates → [[platform-strategy]].

## 1. Price metric — the first decision

| Metric | Examples of fit | Strength | Weakness |
|---|---|---|---|
| Seat / user | collaboration tools | simple, predictable | seat sharing caps ARPA |
| Usage / consumption | infrastructure, APIs | aligned with value | hard to forecast |
| Volume (records, calls) | data pipelines, payments | scales with value | hard to predict before use |
| Feature tier | support and messaging tools | drives upgrades | complexity |
| Outcome | per resolved incident, per booking | best alignment | hard to measure |
| Flat licence | on-premise middleware | buyers like certainty | weak expansion |

Ask three questions: (1) does the unit grow naturally as the customer gets
value? (2) can the customer predict and control it? (3) can it be compared with
competitors? The best metric makes customer success and your revenue grow together.

## 2. Packaging — good-better-best

| Principle | Rule |
|---|---|
| Number of tiers | 3 (GBB); at most 4 including free or enterprise |
| Anchor | the top tier anchors high; most buyers should land on the middle |
| Fence | put the 1–2 most wanted capabilities one tier up |
| Power features | 2–3 premium features pull buyers to the top tier |

```
| Capability        | Good (free/starter) | Better (pro) | Best (enterprise) |
| Core A            | ✓                   | ✓            | ✓                 |
| Power B           | —                   | ✓            | ✓                 |
| Premium C         | —                   | —            | ✓                 |
| Seats / usage     | small cap           | larger cap   | custom            |
| SLA / support     | community           | email        | dedicated         |
| Price             | 0                   | per seat     | contact sales     |
```

Checks: a lower tier must not substitute for a paid one; fewer than 3
differences between adjacent tiers blurs them; publishing enterprise prices
removes negotiation room (a choice to make deliberately).

## 3. Van Westendorp price sensitivity meter

Ask four questions: at what price is it **too cheap** (quality doubt),
**cheap / a bargain**, **expensive but considered**, **too expensive** (won't buy)?

| Intersection | Curves | Meaning |
|---|---|---|
| OPP — optimal price point | too cheap × too expensive | fewest rejections |
| IPP — indifference price point | cheap × expensive | "normal" price |
| PMC — point of marginal cheapness | too cheap × expensive | lower bound |
| PME — point of marginal expensiveness | cheap × too expensive | upper bound |

Acceptable range PMC–PME; sweet spot near OPP. Aim for ≥ 100 respondents per
segment; below 50, do not decide from it.

## 4. Willingness to pay — three methods

| Method | Character | Fits |
|---|---|---|
| Direct survey (Van Westendorp) | stated preference, easy | first sense of range |
| Conjoint analysis | trade-offs between feature bundles | per-feature WTP |
| Live price test (A/B) | revealed preference | most accurate, needs scale |

Simple conjoint: 5–7 features × 2–3 levels, 9–12 paired choices per
respondent, regression to utilities → per-feature WTP and the top 3 features
by utility per cost.

## 5. Hybrid models

| Combination | Design rule |
|---|---|
| Platform fee + usage | fee = commitment to play; usage = pay to scale |
| Seat + usage credits | seat carries base value; usage-heavy features get credits or caps |
| Freemium + upgrade | free builds habit; a clear trigger leads to paid |
| Tiered seats + add-ons | tier sets the baseline; modules sold as add-ons |

One **primary** price metric per product; at most two secondary ones.

## 6. Price-change playbook

| Change | Risk | Mitigation |
|---|---|---|
| Increase for existing customers | churn | grandfathering period (often ~12 months) · value story · single clear notice |
| Repackaging | confusion | migration path · "stay or move" option |
| Metric change (seat → usage) | large churn | run both for a period · win-back plan |
| Shrinking the free tier | reputation | apply to new users only |

Every announcement states: why now · what changes (before/after table) · what
does **not** change · grandfathering terms · where to ask.

## Output structure

1. **Price metric** — choice, three-question rationale, competitor metrics.
2. **Tier table** — 3 tiers × capabilities × price, anchor role stated.
3. **WTP evidence** — method, sample size, PMC–PME range, OPP.
4. **Hybrid design** (if any) — primary + ≤ 2 secondary metrics.
5. **Change plan** (if any) — five announcement elements, grandfathering.
6. **Impact** — LTV/CAC and revenue sensitivity via [[unit-economics-modeling]].

## Worked-example fragment

> *Input:* "Our note-taking app charges $8/user. Teams share logins. What should we do?"

- Diagnosis: seat metric + sharing → ARPA stalls (seat-sharing weakness).
- Option A: keep seats, fence admin controls and SSO in the team tier (removes the sharing incentive for organisations).
- Option B: seat + AI-usage credits; heavy users pay for consumption.
- Evidence needed: Van Westendorp with ≥ 100 team admins; price test on new sign-ups only.
- Change plan for existing users: 12-month grandfathering; "what does not change: your notes and export".

## Constraints

- No tier design before a price metric is chosen.
- No price decision from zero WTP data without stating it is cost-plus.
- No increase without grandfathering terms; no freemium without an upgrade trigger.
- Survey results with N < 50 are not a basis for a decision.
- Final prices are a human decision.

## Output format

Tables for metrics, tiers and intersections; respondent counts and data dates shown with every WTP figure.

## Reason codes + References

- `RC-NO-METRIC` · `RC-FREE-SUBSTITUTES-PAID` · `RC-SMALL-SAMPLE` · `RC-NO-WTP` ·
  `RC-NO-GRANDFATHER` · `RC-TOO-MANY-METRICS` · `RC-NO-UPGRADE-TRIGGER`.
- Sibling packs: [[unit-economics-modeling]] · [[consulting-saas-audit]] · [[gtm-launch-playbook]] · [[platform-strategy]].
