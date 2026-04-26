# ADR 0001 — Initial Architecture Decisions

- **Status**: accepted
- **Date**: 2026-04-26
- **Deciders**: Project Sponsor (peterkimpmp)
- **Supersedes**: —

## Context

Sillok forks key design choices from the upstream PromptOS work in `aipm/`. This ADR records the load-bearing decisions adopted at Phase 0 entry so later changes can be evaluated against them.

## Decisions

| # | Decision | Rationale | Source |
|---|---|---|---|
| D1 | Apache License 2.0 for source; CC BY 4.0 for starter atoms | Permissive + dual-license model used by major AI frameworks | LICENSE / NOTICE |
| D2 | Single-word package name `sillok` on PyPI; org `sillok-os` (the bare `sillok` org is squat-occupied) | AI-framework standard pattern (langchain / dspy / crewai / autogen) | README §License |
| D3 | Vault-resident corpus only — no system-global path | K-6 30-hour ablation: 70% blind-spot in isolated index | README §Why vault-resident only |
| D4 | Two-stage routing (Tier-1 keyword, Tier-2 LLM intent) | ~97% token reduction vs. always-on full context | Top 10 Features #2 |
| D5 | Five retrieval plans, declared per pack | Data-driven retrieval, not heuristic | Top 10 Features #3 |
| D6 | Proposal-only 4-gate governance — auto-growth never overwrites prompts directly | Prevents prompt drift and corpus poisoning | Top 10 Features #4 |
| D7 | Multi-format auto-ingest (md / pdf / docx / xlsx / pptx / txt / hwpx) is the **core loop** | Without it, Features #3 / #8 / #10 decay against a stale corpus | Top 10 Features #1 |
| D8 | MCP-first integration (Tongsa) supporting 7 clients (Claude Code / Codex CLI / Gemini CLI / Cursor / Continue / Claude Desktop / Codex Desktop) | Prevents tool lock-in | Top 10 Features #6 |
| D9 | UNESCO Memory of the World Triple Anchor (Sillok 1997 / Jikji 2001 / Janggyeong 2007) as cultural identity, **not** an endorsement claim | Naming is thematic; NOTICE explicitly disclaims any UNESCO affiliation | NOTICE §3 |

## Consequences

- Changes that contradict any of D1–D9 require a new ADR superseding the relevant clause.
- `GOVERNANCE.md` enforces the proposal-only model on the project itself, mirroring D6.
- The roadmap (Phase 0 ~ Phase 3) is the implementation plan for D1–D9; deviations require an ADR.

## Related

- Phase 0 roadmap: `docs/governance/roadmap.md` (when published) and upstream `aipm/project/Harness-Sillok/03-plan/01-roadmap-and-activation-gates.md`
- Top 10 Features card: `docs/architecture/top-10-features.md` (TBD) and upstream `02-design/06` Part 0.5
