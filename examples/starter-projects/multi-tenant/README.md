# multi-tenant — per-client overlays without re-architecting

The same Sillok install can serve a solo user, a small team, and a
consulting practice with multiple client engagements. The mechanism is
a thin overlay file per scope (`global` / `client:<id>` / `repo:<id>` /
`team:<id>`) that adds, overrides, or hides packs from the global
registry.

> **Status (2026-04-26)**: scope-aware routing engine ships in
> `0.1.0a1+`. Overlay schema is already finalized in
> `sillok.schemas.RegistryOverlay`.

## What this example produces

Two synthetic clients (`acme` and `globex`) with different pack
preferences sharing the same global registry.

```
~/Documents/my-vault/
├── packs/
│   ├── registry.yaml                           # global, 10 starter packs
│   ├── registry-overlay-client-acme.yaml       # acme-specific
│   └── registry-overlay-client-globex.yaml     # globex-specific
└── ...
```

## Steps

```bash
# 1. seed two overlays
mkdir -p ~/Documents/my-vault/packs

cat > ~/Documents/my-vault/packs/registry-overlay-client-acme.yaml <<'EOF'
version: "0.1"
scope: { kind: client, value: acme }
description: Acme — heavy on safety-critical deliverables
add: []
override:
  - id: report-quality
    title: Report Quality (Acme — triangulation ≥ 5 sources/claim)
    path: packs/methodology/report-quality.md
    category: quality-guard
    sub_category: methodology
    precedence: 95   # higher than global to force-attach on every report
    trigger_signals:
      contains: ["report", "audit", "deliverable"]
hide: []
EOF

cat > ~/Documents/my-vault/packs/registry-overlay-client-globex.yaml <<'EOF'
version: "0.1"
scope: { kind: client, value: globex }
description: Globex — strict separation of strategy vs delivery
add: []
override:
  - id: consulting-strategy-audit
    title: Strategy Audit (Globex profile)
    path: packs/consulting/consulting-strategy-audit.md
    category: domain
    sub_category: consulting
    precedence: 92
    trigger_signals:
      contains: ["strategy", "market", "BMC"]
hide:
  - exec-communication      # Globex stakeholders dislike Pyramid-style summaries
EOF

# 2. switch into a scope and route
sillok overlay use --client acme
sillok route "5-part SaaS audit on the analytics platform"
# applied prompt packs: consulting-saas-audit, report-quality(Acme — triangulation ≥ 5)
# scope: client:acme

sillok overlay use --client globex
sillok route "Q3 strategy memo for the board"
# applied prompt packs: consulting-strategy-audit(Globex profile)
# scope: client:globex
# (exec-communication is hidden in this scope)

# 3. or pass scope explicitly per call
sillok route "..." --scope client:acme
```

## When to use overlays

| Use case | Overlay action |
|---|---|
| Same workflow but stricter quality gates per client | `override` on quality-guard pack |
| Client uses different vocabulary (e.g. "BMC" vs "lean canvas") | `override` on `trigger_signals.contains` |
| Internal team has access to packs that customers must not see | `hide` on internal packs in `client:*` scopes, no override at `global` |
| Pilot a brand-new pack with one team before wider rollout | `add` in `team:<id>` scope only |

## Resolution order at routing time

```
priority (high → low):
  1. scope-matched overlay's `add` packs
  2. scope-matched overlay's `override` packs (replaces global by id)
  3. global registry packs (excluding `hide` list from overlay)
  4. (no scope match → fall back to global only)
```

This is implemented in `sillok.schemas.merge_with_global` and consumed
by `sillok.naru` at routing time.

## Inspecting the merged registry

```bash
sillok overlay show --scope client:acme
# Prints the effective registry visible to this scope (post-merge).

sillok overlay diff --scope client:acme --against global
# Shows what acme adds/overrides/hides relative to the global registry.
```

## Non-goals

- Authentication / authorization across overlays — Sillok scope is a
  routing concept, not a security boundary. RBAC is the host system's
  responsibility (see `docs/governance/security-model.md` when published).
- Conflict detection between two overlays — only a single overlay is
  active per route call.
