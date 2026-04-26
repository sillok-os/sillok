# Governance

Sillok runs on a **proposal-only model** — the same discipline the codebase enforces on prompts (Top 10 Feature #4) is applied to project decisions.

## Roles

| Role | Authority |
|---|---|
| **Project Sponsor** | Peter Kim (peterkimpmp). Final tie-break during the pre-Steering-Group phase. |
| **Maintainers** | Merge rights on `main`. Required count grows from 1 (today) to ≥3 before v1.0.0 GA. |
| **Contributors** | Anyone with a merged PR. Listed in `CONTRIBUTORS.md` once that file is created. |
| **Steering Group** | Forms when ≥5 active contributors exist. Reviews ADRs and roadmap changes. |

## Decision pipeline

All non-trivial changes follow the same 4-gate as the engine itself:

1. **Artifact** — proposal as PR or ADR (`adr/NNNN-*.md`)
2. **Schema** — passes lint and type checks
3. **Shadow** — passes eval suite (when wired in F0.7+) without regression
4. **Human** — at least one maintainer approval; for ADR-class changes, two

Trivial changes (typo, lint, test-only) skip steps 1–3 and need only one approval.

## Architectural Decision Records (ADR)

ADRs live in `adr/`. Numbering is sequential. Status values: `proposed` / `accepted` / `superseded` / `rejected`. Once accepted, an ADR is not edited; instead, a new ADR supersedes it.

## Roadmap authority

The roadmap (`docs/governance/roadmap.md`, mirrored in upstream `aipm/project/Harness-Sillok/03-plan/01-roadmap-and-activation-gates.md`) is the source of truth for what ships when. Changes to the roadmap require an ADR.

## Release authority

Pre-1.0: the Project Sponsor cuts releases. Post-1.0: any maintainer may cut a patch release; minor and major releases require ADR + Steering Group sign-off.

## Conflict resolution

Disagreements among maintainers escalate to the Project Sponsor (pre-Steering-Group) or the Steering Group (post-formation). Decisions are recorded as ADRs.

## Code of Conduct

See [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md). Reports are handled by the Project Sponsor until the Steering Group forms.
