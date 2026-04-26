# Governance

Sillok runs on a **proposal-only model** — auto-growth and eval feedback
never overwrite system prompts directly. The same discipline applies to
the project itself.

## Documents

- [`GOVERNANCE.md`](https://github.com/sillok-os/sillok/blob/main/GOVERNANCE.md) — roles, decision pipeline, ADR process, release authority
- [`CONTRIBUTING.md`](https://github.com/sillok-os/sillok/blob/main/CONTRIBUTING.md) — DCO sign-off, scope discipline checklist
- [`CODE_OF_CONDUCT.md`](https://github.com/sillok-os/sillok/blob/main/CODE_OF_CONDUCT.md) — Contributor Covenant 2.1 by reference
- [`SECURITY.md`](https://github.com/sillok-os/sillok/blob/main/SECURITY.md) — private vulnerability reporting
- [`NOTICE`](https://github.com/sillok-os/sillok/blob/main/NOTICE) — third-party trademarks, attributions, cultural references
- [`adr/`](https://github.com/sillok-os/sillok/tree/main/adr) — Architectural Decision Records (start with `0001`)

## The 4 gates

Every proposal — whether to a pack body, the registry, the schema, or
this documentation — passes the same four gates before merge:

1. **Artifact** — proposal as PR or ADR
2. **Schema** — passes lint and type checks
3. **Shadow** — passes eval suite without regression
4. **Human** — at least one maintainer approval (two for ADR-class)

Trivial changes (typo, lint, test-only) skip steps 1 ~ 3 and need only
one approval.

## Roles (current → target)

| Role | Today | Target (post v1.0.0) |
|---|---|---|
| Project Sponsor | 1 (Peter Kim) | 1, with veto on safety / license |
| Maintainers | 1 | ≥ 3 |
| Steering Group | not yet formed | forms when ≥ 5 active contributors |
| Working Groups | none | optional, by ADR |

## ADR life-cycle

```
proposed  →  accepted  →  (later)  superseded
                         \
                          rejected
```

Once accepted, an ADR is **not** edited; supersession is the only path.
Numbering is sequential and gap-free.

## See also

- Phase / roadmap: see `docs/governance/roadmap.md` (when published) or
  upstream `aipm/project/Harness-Sillok/03-plan/01-roadmap-and-activation-gates.md`
- Trademarks and attributions: `NOTICE`
- Top 10 features (Feature #4 governance): `README.md`
