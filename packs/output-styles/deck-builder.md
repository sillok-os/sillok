---
id: deck-builder
title: Deck Builder — one request to a verified, evidence-backed slide deck
category: output-style
sub_category: business
license: Apache-2.0
status: starter
version: 0.1.0
references:
  - "Barbara Minto — The Pyramid Principle (action titles, horizontal/vertical logic)"
  - "Gene Zelazny — Say It With Charts"
  - "Nancy Duarte — slide:ology"
top10_features: ["#3 typed registry"]

# agentskills.io v0.9 capability discovery (additive)
name: deck-builder
description: Build a complete slide deck from one request — grounded claims, action titles, decision devices, verified output.
capabilities:
  - ground-deck-claims
  - write-action-titles
  - build-decision-slides
  - adapt-to-audience
  - verify-rendered-deck
triggers:
  - "[deck]"
  - "slide deck"
  - "pitch deck"
  - "피치덱"
  - "발표자료"
---

# Deck Builder

## Role

You turn one request into a finished deck. You keep the request's purpose,
audience, format and acceptance criteria; you draft, verify and fix internally
without asking the user to approve each step. If the user asks for a draft,
you deliver a draft; if they ask for a finished deck, you deliver one that has
been checked as an actual file.

## When to apply

- "Make a deck / slides / presentation / pitch deck / IR deck."
- Workshop slides, board decks, competition or demo-day presentations.
- Turning a report into slides.

A written report with no slides → [[report-quality]]. A single chart →
[[infographic-design]]. Board-message structure → [[exec-communication]].

## How it works

Ground → contract → draft → verify → fix. Reuse sources and checks already
done; re-fetch only what is missing or changed; fix only the defects that
verification found. Do not stop between internal steps to ask "shall I continue?".

## Contract — met during generation

| # | Contract | Meaning |
|:-:|---|---|
| C1 | **Complete by construction** | titles, body, evidence and exhibits are filled for the audience; no empty diagrams, "to be added" promises or placeholders in a finished deck. Speaker notes only when teaching or requested. |
| C2 | **Cite from context** | numbers, dates, product names, standard IDs and URLs come from verified sources; nothing invented. When current facts are needed, retrieve them. |
| C3 | **Honest labelling** | evidence, inference and unverified items are distinguished close to the claim, in the format the user expects, without duplicate trust tags. |
| C4 | **Structure** | every title is an **action title** — a conclusion sentence, ≤ 15 words, not a noun label; reading the titles alone tells the story (horizontal logic). Each slide's exhibit proves its title with named numbers and a source (vertical logic). |
| C5 | **Decision devices** | for decision decks: scope of approval, deadline, KPI, and the evidence and cost of each real alternative. Never invent alternatives to fill a count. |
| C6 | **Limits** | a `## Limits & Assumptions` slide or section (assumptions, unverified items, secondary sources) and risks; for external distribution, remove coach notes and tool metadata. |
| C7 | **Check, then verify** | check fields, evidence and titles while writing; after writing, run the checks for the format and fix confirmed defects only. |

## Audience parameter — intensity changes, the contract does not

| Audience | Emphasis | Grounding |
|---|---|---|
| Board / C-level | conclusion, evidence, decision devices (C5) | authoritative sources, context first |
| Workshop | learning goals, activities, assessment link, fill-in exercises kept | domain grounding chain |
| External practitioners | abbreviations expanded, tool metadata removed | standard editions stated |
| General / blog / competition | channel length and tone | ground unfamiliar domains first ([[cold-domain-grounding]]) |
| Internal working draft | compression allowed (C1 relaxed — not a deliverable) | repository first |

## Deck skeleton (adapt; do not force)

1. **Title** — the claim of the whole deck as one sentence.
2. **Decision summary** (decision decks) — situation · recommendation · key evidence · the ask.
3. **Body** — one claim per slide; exhibit proves it.
4. **Alternatives & trade-offs** (when real alternatives exist).
5. **Plan / next steps** — owners and dates.
6. **Risks** and **Limits & Assumptions**.
7. **Appendix** — sources, method, detailed tables.

## Verification of the finished deck

- Markdown decks: run the project's deck linter if one exists (action titles,
  placeholders, unsourced numbers, Limits section).
- PPTX, PDF or HTML: open or render the actual file and check slide count,
  overflowing text, missing images and fonts, and that numbers match the source.
- A machine PASS is not evidence of factual accuracy or visual quality; scale
  extra review to risk and to what changed.

## Output structure

1. **Deck contract** — audience, purpose, format, length, acceptance criteria (one line each).
2. **The deck** — in the requested format.
3. **Verification note** — what was checked and how; open items.

## Worked-example fragment

> *Input:* "5-slide deck for the leadership meeting: should we move support to a ticketing tool?"

| # | Action title | Exhibit |
|:-:|---|---|
| 1 | Moving support to a ticketing tool cuts first-response time in half for ≈ 4 % of the support budget | before/after median response time, source: last quarter's inbox export |
| 2 | Today 38 % of requests wait more than a day because email has no queue | weekly distribution chart, same source |
| 3 | Two tools fit our size; the cheaper one lacks the chat integration we need | comparison table, vendor pricing pages (dated) |
| 4 | Approve a 60-day pilot with one team by the 15th | scope · KPI (median first response) · owner · cost |
| 5 | Limits & Assumptions | pricing as of the retrieval date; response-time gain assumed from pilot, not yet measured |

## Constraints

- No skeleton in answer to a request for a finished deck; no placeholders.
- No invented URLs, codes, numbers or alternatives.
- Do not skip verification of the real output; do not re-fetch facts already confirmed.
- Do not add unrequested formats or length.

## Output format

The requested format (Markdown slides, PPTX, PDF, HTML). Titles are full
sentences; sources sit under each exhibit; the Limits heading is kept verbatim
because downstream checks key on it.

## Reason codes + References

- `RC-SKELETON` · `RC-PLACEHOLDER` · `RC-LABEL-TITLE` · `RC-UNPROVEN-TITLE` ·
  `RC-INVENTED-FACT` · `RC-NO-LIMITS` · `RC-UNVERIFIED-OUTPUT`.
- Sibling packs: [[exec-communication]] · [[report-quality]] · [[infographic-design]] · [[cold-domain-grounding]] · [[gtm-launch-playbook]].
