# Extending Sillok with your domain

> **Audience.** Anyone who wants to add a new pack — covering an industry vertical (Banking, Insurance, Automotive, Medical Device, Embedded, …), a methodology family (NIST RMF, FAIR, Change Management, Org Design, …), or a specialty practice (M&A diligence, Pricing, GTM, Growth, UX research, …) — to Sillok.

The starter `0.1.0a4` ships **7 of the 25 categories** in the [framework coverage inventory](../architecture/framework-coverage.md). The remaining 17–18 categories are intentionally left for **domain SMEs** — that's you, if you're reading this. This guide covers both contribution paths:

- **External contributor track** — you don't have commit rights; you open a PR.
- **Maintainer SME track** — you do have commit rights and you're back-porting from a real consulting engagement.

Most of the procedure (sanitization, ship-status, citations) is identical between the two tracks. Where they differ, this guide calls it out explicitly.

---

## 1. Decide what you're adding

Pick exactly one of:

| Form | Example | Effort |
|---|---|---|
| **New pack** in an existing category | A `change-management` pack body for category 7 (currently 🚧 queued) | 2–8 hours |
| **New category** (and its first pack) | `automotive-standards` pack for category 9 (currently ⏳ queued) | 6–16 hours (more if industry-specific evidence is dense) |
| **Pack body** for an existing registry entry | A real body for a stub already declared in `packs/registry.yaml` | 4–12 hours |
| **Pack revision** | Tightening an existing pack with a new framework or correction | 1–4 hours |

If your contribution doesn't fit one of these forms, open a [Discussion](https://github.com/sillok-os/sillok/discussions) first — pack registry shape is governance-bound and ad-hoc additions tend to drift.

---

## 2. Pack anatomy

Every pack is a single Markdown file at:

```
packs/<sub_category>/<pack_id>.md
```

`<sub_category>` is one of `consulting/`, `core/`, `methodology/`, `output-styles/` (existing today). New top-level sub-categories are allowed but require an ADR — propose them in a Discussion first.

### Required frontmatter (sillok pack frontmatter v1)

```yaml
---
id: <pack-id-kebab-case>          # required, unique across the registry
title: <Human-readable title>
category: <one of: domain | workflow | output-style | methodology | follow-up>
sub_category: <consulting | core | methodology | output-styles | ...>
license: Apache-2.0                # source license of the pack body
status: starter | candidate | stable
version: 0.1.0a4                  # Sillok version when this body was authored
references:
  - "<Standard name with year>"   # nominative, see §5
  - "<Author. Title (Year). Publisher.>"
top10_features: ["#3 typed registry"] # which Top-10 features the pack exercises
---
```

### Required body sections

```markdown
# <Pack Title>

## Role
You are a pack that ... (one sentence)

## <Methodology core sections — 3 to 8>
The actual methodological content. Tables, diagrams, code blocks
allowed. Do **not** invent frameworks; only use ones cited in
`references:` above.

## Output format (your reply)
What the pack should emit when invoked. Always include the line
"applied prompt packs: <pack-id>" first.

## Constraints
What this pack must never do (anti-patterns specific to the
methodology).

## Examples
At least one worked example showing input → output.

## Reason codes
| Code | Meaning |
|------|---------|
| R1 | explicit `[<keyword>]` trigger |
| R2 | ... |
```

The 10 starter packs in `packs/` are the canonical reference shape — read at least two before writing yours.

---

## 3. registry.yaml entry

Add a new entry under `packs:` in `packs/registry.yaml`. Required keys:

```yaml
  - id: your-pack-id
    title: Your Pack Title
    category: domain                # see frontmatter taxonomy
    sub_category: methodology
    body_path: packs/methodology/your-pack-id.md
    precedence: 100                 # 100=normal, 50=fallback-only, 200=must-load
    triggers:
      keywords:
        - "<keyword 1>"
        - "<keyword 2>"
      regexes: []                   # optional, more precise but slower
    corpus_affinity:
      retrieval_plan: vault_first   # one of: vault_first |
                                    #   vault_then_llmwiki_fallback |
                                    #   llmwiki_recovery_first |
                                    #   dual_compare | no_corpus
    status: starter | candidate | stable
    version: 0.1.0a4
    discovery_tier: 2               # 1=always-loaded, 2=on-demand
```

Validate before commit:

```bash
python -c "import yaml, sillok.schemas as s; \
  s.RegistrySchema.model_validate(yaml.safe_load(open('packs/registry.yaml')))"
```

(Schema validation is wired in `sillok.schemas`; see `tests/unit/schemas/` for examples.)

---

## 4. Sanitization checklist (the most important step)

Sillok is OSS; pack bodies are world-readable. Before you commit, scrub these five categories — failure here is the most common reason a PR gets sent back.

### 4.1 Client identifiers

- **Remove**: company names, project codenames, internal team names, individual names, email addresses, phone numbers.
- **Replace with**: `Acme`, `Globex`, `Initech`, or generic role nouns (`the client`, `the platform team`).

### 4.2 Confidential numbers

- **Remove**: revenue, headcount, valuation, salary, churn rate, client-specific KPI thresholds.
- **Replace with**: order-of-magnitude bands (`$10–100M ARR`, `1,000–10,000 employees`) or remove the example entirely.

### 4.3 Internal URLs / paths

- **Remove**: anything pointing to your private vault (`~/Documents/...`), your company intranet (`https://confluence.<corp>...`), or staging environments.
- **Replace with**: `https://example.com/...` or generic placeholders.

### 4.4 Closed methodology IP

If you're a partner at a consulting firm, **your firm's proprietary frameworks are not yours to publish**. Stick to:
- Public standards (ISO, IEC, NIST, COSO, PMI, IATF, AUTOSAR, FDA, …)
- Published author works **with citation** (Porter, Kotter, Christensen, Ulrich, …)
- Your own published work (with citation)

If a proprietary framework is *the* core of your domain (e.g. McKinsey 7-S — actually public; vs. Bain Net Promoter® — trademark-bound), keep the public public-domain rendition only.

### 4.5 Country-/jurisdiction-locked compliance details

If your pack covers a regulation specific to one jurisdiction (PIPL = China, K-ISMS-P = Korea, DORA = EU), keep the **regulation summary** but mark which jurisdiction it applies to. Don't generalize a Korea-only rule as worldwide.

### Maintainer SME shortcut

If you're back-porting from a real engagement (maintainer SME track), the easy version is:

```bash
# 1. Copy your sanitized internal pack into the mirror
cp ~/private/playbooks/banking-risk-pack.md \
   project/Harness-Sillok/mirror/packs/methodology/banking-risk-standards.md

# 2. Run a content sweep before staging
grep -E "<your-corp>|<client>|@<corp>\.com|\$[0-9]+M ARR" \
   project/Harness-Sillok/mirror/packs/methodology/banking-risk-standards.md
# Should return zero hits before you proceed.

# 3. From inside mirror/, follow the rest of this guide.
cd project/Harness-Sillok/mirror
```

---

## 5. Standards citation rule (nominative fair use)

Every framework or standard you cite must be **named accurately** and **disclaimed**. The accepted boilerplate, kept in `NOTICE`:

> Sillok references `<Standard / Framework Name>®` under nominative fair use; Sillok is not affiliated with or endorsed by `<Standards Body / Author>`.

You don't need to repeat this disclaimer in every pack — `NOTICE` covers it. But if you add a *new* trademark (e.g. `Six Sigma®`, `Lean Startup®`) that wasn't already in `NOTICE`, **append it to NOTICE in the same PR**.

Citation format inside the pack body:

```markdown
- **PMBOK 8** (PMI 2021) — 8 Performance Domains, 12 Principles
- **ISO 26262:2018** — Functional Safety, HARA + ASIL classification
- **Porter** — *Competitive Strategy* (1980), Five Forces analysis
```

Year, publisher, and the bit you're using. No "industry best practice" without an attributable source.

---

## 6. Update the framework coverage inventory

Two files must move together when you add a pack:

### 6.1 `docs/architecture/framework-coverage.md`

- Find the row for your category in the *Ship status per category* table.
- Move the glyph from `🚧` or `⏳` to `✅` (or `◐` if partial).
- Add the standards your pack covers to the *Standards* column.
- If you added a brand-new category that isn't in the 25, **propose it in an issue first** — the 25-category structure is governance-bound.

### 6.2 README (both EN and KO)

- Update the *Framework coverage* ASCII picture if a category status changed.
- Add a row to the *What ships in 0.1.0a3 today* table (or whichever version yours becomes).
- Update the *Persona pairing* excerpt if your pack changes which role can use which category.

> **EN/KO parity is mandatory** — both READMEs must move together. The `README.ko.md` companion is not optional decoration; bilingual support is part of Sillok's identity (see the `README.ko.md` opener — preserved Korean module vocabulary).

---

## 7. Quality gate

Before opening a PR, run:

```bash
# 1. Schema + registry validation
python -c "import yaml, sillok.schemas as s; \
  s.RegistrySchema.model_validate(yaml.safe_load(open('packs/registry.yaml')))"

# 2. Sanitization sweep (zero hits expected)
grep -RnE "(<your-corp>|<client-name>|@yourorg\.com|\$[0-9]+M ARR)" packs/

# 3. Tests
ruff format packs/ docs/
ruff check packs/ docs/
pytest tests/unit/bongsu tests/unit/yeonryun tests/integration/ -q

# 4. Pack discoverable by the router
python -m sillok.naru.router_2tier --message "<a query that should hit your pack>"
# Expected: your-pack-id appears in `applied prompt packs:`.

# 5. Pack searchable by bongsu (if your pack body has trigger keywords)
python -m sillok.bongsu.search --vault packs/ --query "<keyword>" --format full
```

All five must pass.

---

## 8. PR workflow

### External contributor

1. Fork → topic branch (`feat/<category>-<pack-id>` e.g. `feat/automotive-iso26262`).
2. Commits sign-off (`git commit -s`) — DCO is mandatory.
3. PR title: `feat(packs/<sub_category>): add <pack-id> for <category>`.
4. PR body must include:
   - **Category** addressed (1 of 25 from the inventory)
   - **Standards covered** (with year + source)
   - **Sanitization sweep result** (paste the `grep` zero-hit output)
   - **Quality gate output** (paste the 5-step result)
   - **Persona pairing** (which row in framework-coverage.md §3 is enabled by this pack)
5. Wait for review. Maintainers will run the proposal-only governance pipeline (Sangso, when wired).

### Maintainer SME track

Same as external, plus:

- Mirror operating model rules apply (`00-meta/10-mirror-operating-model.md`): edit inside `aipm/project/Harness-Sillok/mirror/`, push from there.
- **Skip the fork**, push to a topic branch on `sillok-os/sillok` directly.
- Self-review is forbidden — get a second reviewer (or a structured eval probe pass) before merging. If you're the only maintainer, document this in the merge commit and revisit when the reviewer pool widens.

---

## 9. After merge

A merged pack triggers three follow-ups, all owned by maintainers:

1. **Patch alpha release** — version bump, CHANGELOG entry, tag, GH Release. Even single-pack additions warrant a `0.1.0aN+1` so PyPI and GitHub stay in sync.
2. **Eval probe addition** — when `gwageo` runner lands (Phase 1 PR-B), every pack must have at least one golden probe. New packs added before then are tracked in `tests/probes/_pending/`.
3. **Persona-pairing review** — if your pack opens a new persona row in framework-coverage.md §3, the maintainer reviews whether a *pre-existing* pack already implicitly served that persona; if so, the older pack is annotated to point at the new specialization.

---

## 10. Common pitfalls

| Pitfall | Symptom | Fix |
|---|---|---|
| Pack body cites methodology by acronym only | Reader can't tell what's referenced | Spell out on first use + add to `references:` frontmatter |
| `precedence` set to 200 ("must-load") | Router pulls your pack on every query | Use 100 unless ADR justifies otherwise |
| Trigger keywords too generic (`"strategy"`) | Pack fires for unrelated queries | Use 2-3 word phrases or regex anchors |
| Citation without year | Auditors flag the pack | Year + publisher mandatory |
| README updated but framework-coverage.md not | Inventory drifts from README | Both files move in the same commit |
| KO README skipped | Bilingual parity broken | Both READMEs in the same commit |
| Sanitization grep skipped | Client name leaks to OSS | Run the sweep — zero hits before commit |
| Pack added but no test | CI passes but pack fails in the wild | At minimum a router smoke + a body validation test |

---

## See also

- [`CONTRIBUTING.md`](../../CONTRIBUTING.md) — DCO, code style, scope discipline.
- [`docs/architecture/framework-coverage.md`](../architecture/framework-coverage.md) — the 25-category inventory you're filling.
- [`packs/registry.yaml`](../../packs/registry.yaml) — the source of truth for what's currently registered.
- [`NOTICE`](../../NOTICE) — trademark and citation manifest you append to.
- [`GOVERNANCE.md`](../../GOVERNANCE.md) — proposal-only review pipeline.
