# ADR 0002 — Routing claims corrected to match the implementation

- **Status**: accepted
- **Date**: 2026-11-21
- **Deciders**: Project Sponsor (peterkimpmp)
- **Supersedes**: ADR 0001 D4 (wording and rationale); clarifies ADR 0001 D5

## Context

Preparing a paper on Sillok, we checked the public routing claims against the code and a measurement.

- Tier 2 was described as LLM intent classification. `sillok/naru/router_2tier.py` makes no model call: Tier 1 scores packs by deterministic keyword matching, and Tier 2 loads the bodies of the selected packs. `naru.action_layer.classify_action` is also a keyword heuristic.
- "~97% token reduction vs. always-on full context" had no reproducible measurement. On the 59 router golden messages, the Tier-1 summaries plus the selected pack bodies take about 94% fewer tokens than loading all 47 pack bodies (mean 93.8%, median 94.1%, minimum 91.1%; characters divided by four). This compares pack instructions only, not the whole context window.
- "Every pack declares its `retrieval_plan`": `bongsu` supports the five plan IDs, but none of the 47 starter packs declares one. Sample outputs also used `wiki_first`, which is not one of the five IDs.

## Decision

| # | Revised decision | Rationale |
|---|---|---|
| D4 | Two-stage routing: Tier 1 deterministic keyword match, Tier 2 body load of the selected packs. No model call while routing. | Reproducible, auditable and free to run. Measured pack-instruction saving is about 94% against loading every pack body. |
| D5 | Five retrieval plan IDs that a pack may declare. Starter packs do not declare one yet. | Plans stay data, not heuristics, once packs declare them. |

An LLM- or embedding-based routing tier, if added, needs its own ADR and an accuracy measurement against labelled prompts.

## Consequences

- README, README.ko, STATUS, docs/index, the `naru` README and the CHANGELOG are corrected in the same change.
- Public figures about routing state how they were measured.
