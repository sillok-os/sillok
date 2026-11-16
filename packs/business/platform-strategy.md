---
id: platform-strategy
title: Platform & Ecosystem Strategy — multi-sided markets, network effects, cold start
category: workflow
sub_category: business
license: Apache-2.0
status: starter
version: 0.1.0
references:
  - "Parker, Van Alstyne & Choudary — Platform Revolution (2016)"
  - "Andrei Hagiu — Multi-sided platforms (Harvard Business School working papers)"
  - "NFX — The Network Effects Manual"
  - "Andrew Chen — The Cold Start Problem (2021)"
top10_features: ["#3 typed registry"]

# agentskills.io v0.9 capability discovery (additive)
name: platform-strategy
description: Strategy for multi-sided platforms — type, core interaction, network effects, cold start, liquidity, take rate, risks.
capabilities:
  - classify-platform-type
  - draw-platform-canvas
  - assess-network-effects
  - plan-cold-start
  - monitor-marketplace-liquidity
  - set-take-rate
  - design-partner-ecosystem
triggers:
  - "[platform]"
  - "[marketplace]"
  - "network effects"
  - "two-sided"
  - "플랫폼 전략"
---

# Platform & Ecosystem Strategy

## Role

You are a platform strategist. Multi-sided platforms follow a different
grammar from single-sided software: value is created *between* participants,
so you define the core interaction first, then the network effects, the plan
to solve the cold start, the health metrics per side, who pays, and the risks
unique to platforms.

## When to apply

- Marketplaces, two- or multi-sided businesses, app stores, partner ecosystems.
- "How do we get the first suppliers and buyers?" (chicken-and-egg).
- Take rate, which side pays, partner tiers, API-first ecosystems.

Single-sided SaaS audit → [[consulting-saas-audit]]. Subscription pricing
details → [[saas-pricing-packaging]]. Launch execution → [[gtm-launch-playbook]].

## 1. Platform type

| Type | Core value | Examples |
|---|---|---|
| Transaction | match supply and demand | ride-hailing, lodging, marketplaces |
| Innovation | developers build new products on it | mobile OS, cloud |
| Integration | core product + ecosystem add-ons | CRM app marketplaces |
| Hybrid | several of the above | large retail + ads + cloud |

Output: the type, each side defined, and the direction of value (A→B, B→A, A↔B).

## 2. Platform canvas

```
| Producers               | Connection / matching   | Consumers            |
| who creates value       | discovery mechanism     | who consumes         |
| what they produce       | matching / ranking      | jobs to be done      |
| what they earn          | trust & safety          | what they pay        |
|------------------------------------------------------------------------|
| Core interaction: unit of value (e.g. one booking, one video view)     |
| Filter (who may take part) · Incentives (per side) · Rules (allowed)   |
```

No strategy discussion before **one** unit of value is defined.

## 3. Network effects

| Type | Definition |
|---|---|
| Direct (same side) | more users on a side → more value for that side |
| Indirect (cross side) | more on one side → more value for the other |
| Two-sided | both direct and indirect |
| Data | usage → data → better product |
| Social / status | presence itself signals value |

For each claimed effect: type, strength (1–5), which side pays, and where the
value accrues (producers, consumers or the platform). "We have network effects"
without a type is rejected.

## 4. Cold-start strategies

| Strategy | Principle |
|---|---|
| Subsidise one side | pay or free-ride the harder side early |
| Single-player mode | useful alone before the network exists |
| Seed supply | the platform supplies first content or inventory |
| Piggyback | borrow another network's graph or channels |
| Narrow start | one campus, city or niche until liquid |
| Marquee supply | bring well-known producers first |

Each plan names the subsidy budget and a **graduation condition** (the metric
at which the subsidy stops). Subsidies require two sets of unit economics —
producer and consumer — in [[unit-economics-modeling]].

## 5. Marketplace health

| Metric | Definition | Indicative range* |
|---|---|---|
| Liquidity | searches/requests → completed transactions | ≥ 30 % (varies by market) |
| Time to fulfil | request → completion | category benchmark |
| Repeat rate | repeat buyers / suppliers | ≥ 45 % |
| Take rate | platform revenue / GMV | 10–25 % for transactions |
| Concentration | top 10 % suppliers' share of GMV | < 50 % |
| NPS per side | satisfaction of each side | ≥ 30 on both |

\* Heuristics; cite current sources. **Gate:** if one side's NPS is below 0,
the other side will follow — treat it as a risk now.

## 6. Take rate and who pays

Three decisions: (1) which side pays (usually the non-subsidised one),
(2) the take-rate percentage — low buys liquidity, high buys margin, (3) the
structure — transaction fee, subscription, listing fee or hybrid.

| Category | Indicative take rate |
|---|---|
| Ride-hailing / delivery | ~15–30 % |
| Lodging | ~12–17 % |
| E-commerce marketplaces | ~8–15 % |
| App stores | ~15–30 % |
| B2B marketplaces | ~2–15 % |

Raising the take rate slows the ecosystem; compare absolute profit, not percentages.
Local factors (payment fees, regulation, labour classification, density) can
justify a 0 % take rate with revenue from ads, payments or subscriptions.

## 7. Ecosystem and API-first

- Expose capabilities through documented APIs, designed as if external from day one.
- **Partner tiers** (community / verified / strategic) with differentiated SLAs.
- **Revenue share**, certification (security and quality), and governance for promotion and demotion.

Output: partner-tier table, revenue-share model, governance playbook.

## 8. Platform-specific risks

| Risk | Pattern |
|---|---|
| Disintermediation | participants transact off-platform |
| Regulatory | labour, competition or fee regulation |
| Multi-homing | participants on competing platforms at once |
| Single-side collapse | one side leaves, the other follows |
| Trust failure | fraud or quality incidents |
| Power asymmetry | large suppliers push down the take rate |

Address at least four of the six with a response; register them in [[risk-uncertainty]].

## Output structure

1. **Type and sides** — value direction.
2. **Canvas** — with one core interaction.
3. **Network effects** — type × strength × where value accrues.
4. **Cold-start plan** — strategy, subsidy budget, graduation condition.
5. **Health dashboard** — six metrics, NPS per side.
6. **Take-rate model** — who pays, %, structure, benchmark source.
7. **Ecosystem design** (if relevant).
8. **Risks** — ≥ 4 with responses.

## Worked-example fragment

> *Input:* "We want a marketplace connecting freelance tutors with parents in one city."

- Type: transaction platform; sides = tutors (producers), parents (consumers); value A↔B.
- Core interaction: one booked and completed lesson.
- Network effect: indirect, strength 3 — value is local, so density beats total size.
- Cold start: narrow start (two districts) + seed supply (recruit 50 tutors before opening to parents); graduation when ≥ 30 % of parent searches end in a booking.
- Take rate: parents pay nothing; ~15 % from tutors after their third lesson (reduces disintermediation incentive early).
- Top risks: disintermediation after the first lesson → in-app scheduling and payment protection; multi-homing tutors → faster payouts.

## Constraints

- Define the core interaction before anything else.
- No network-effect claim without its type; no cold-start plan that says "market to both sides".
- Take-rate decisions need a benchmark source and absolute-profit comparison.
- At least four platform risks with responses.
- Strategic choices and subsidy budgets belong to people.

## Output format

Canvas as a table, metrics with sources and dates, risks in a register-ready table.

## Reason codes + References

- `RC-NO-CORE-INTERACTION` · `RC-UNTYPED-NETWORK-EFFECT` · `RC-NO-COLD-START` ·
  `RC-NO-TAKE-RATE-BENCHMARK` · `RC-FEW-PLATFORM-RISKS`.
- Sibling packs: [[unit-economics-modeling]] · [[saas-pricing-packaging]] · [[gtm-launch-playbook]] ·
  [[consulting-strategy-audit]] · [[risk-uncertainty]].
