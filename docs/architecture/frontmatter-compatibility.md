# Frontmatter Compatibility — Native Sillok + agentskills.io v0.9

> **Status**: shipped in v0.2.0a1 · Issue [#2](https://github.com/sillok-os/sillok/issues/2)
> **Schema**: `sillok.schemas.SkillsV09Frontmatter`
> **Validator**: `python -m sillok.schemas validate-skills`

## Why two schemas

Sillok's native pack frontmatter (`id` / `title` / `category` / `sub_category` / `version` / `references` / `top10_features`) is shaped around the **router and registry contract** — what Sillok needs to make routing decisions and to manage pack lifecycle.

agentskills.io v0.9 (`name` / `description` / `capabilities` / `triggers`) is shaped around **third-party capability discovery** — what tools like Cursor, Continue, Codex CLI, and ChatGPT Desktop need in order to surface a pack as a callable skill.

Rather than force one schema to do both jobs, every pack body declares **both** in the same frontmatter block. The two schemas coexist as additive layers.

## How it looks in a pack body

```yaml
---
# Native Sillok schema
id: pm-enhanced
title: PM Lifecycle Pack — Plan / Doing / Done / Release / Audit
category: domain
sub_category: methodology
license: Apache-2.0
status: starter
version: 0.1.0a1
top10_features: ["#2 routing", "#3 retrieval-plan vault_first", "#10 failure taxonomy + replay"]

# agentskills.io v0.9 capability discovery (additive)
name: pm-enhanced
description: PM lifecycle coach — Plan/Doing/Done/Release/Audit with issue-tracker artifacts and 5-class failure taxonomy.
capabilities:
  - route-pm-message
  - emit-lifecycle-artifact
  - sync-issue-state
  - emit-failure-taxonomy
triggers:
  - "[pm]"
  - "$pm-todo"
  - "$pm-doing"
  - "$pm-done"
  - "milestone"
  - "release"
  - "retrospective"
---
```

## Field-by-field guidance (v0.9)

| Field | Rule | Source |
|---|---|---|
| `name` | Must equal the native `id`. | Stable identifier across both schemas. |
| `description` | Single line, ≤ 120 characters. | Shown in tool pickers; keep it concrete and verb-led. |
| `capabilities` | Verb-noun phrases (e.g., `route-pm-message`). | Capability-aware clients ground their tool routing on these. |
| `triggers` | Natural-language phrases or canonical command tokens (e.g., `[pm]`). | Compatible with the native `trigger_signals` block in `registry.yaml`. |

## What reads what

| Reader | Reads native fields | Reads v0.9 fields |
|---|:---:|:---:|
| `sillok.naru.router_2tier` | ✅ | — |
| `sillok.bongsu.search` | ✅ | — |
| `sillok.schemas.RegistrySchema` | ✅ | — |
| Cursor / Continue / Codex CLI capability discovery | — | ✅ |
| `sillok.schemas.SkillsV09Frontmatter` validator | — | ✅ |

The two readers never collide — each ignores the other's fields.

## Validating

```bash
# Validate every pack body declares v0.9 frontmatter
python -m sillok.schemas validate-skills

# Strict mode (default) — fails on missing v0.9 fields
python -m sillok.schemas validate-skills --strict

# Permissive — skip files without v0.9 fields, validate the rest
python -m sillok.schemas validate-skills --no-strict
```

The unit test `tests/unit/schemas/test_skills_v09.py::test_all_starter_packs_carry_v09_frontmatter` enforces the same contract in CI.

## Migration path to v1.0.0 GA

When agentskills.io reaches v1.0 and stabilizes, Sillok will:

1. Adopt v1.0 fields additively (same pattern as v0.9 → today).
2. Mark v0.9 fields as deprecated for ≥ 1 minor release.
3. Provide a `python -m sillok.schemas migrate-skills v0.9 v1.0` codemod.
4. Drop v0.9 fields no earlier than `0.4.0`, after at least one full release advertising the deprecation.

Until then, treat both schemas as load-bearing.
