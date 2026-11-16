---
id: visual-quality
title: Visual Quality — hierarchy, contrast, accessibility, states, motion, print and release gate
category: quality-guard
sub_category: visual
license: Apache-2.0
status: starter
version: 0.1.0
references:
  - "W3C — WCAG 2.2 Level AA"
  - "Deque — axe-core accessibility rules"
  - "W3C — Media Queries Level 5 (prefers-reduced-motion)"
  - "W3C — CSS Paged Media Module Level 3"
  - "nexu-io/open-design — craft guidance (Apache-2.0), used as inspiration"
top10_features: ["#3 typed registry", "#8 eval golden probes"]

# agentskills.io v0.9 capability discovery (additive)
name: visual-quality
description: Self-check any visual output (HTML, slides, PDF, image) on V1–V8 and anti-patterns before calling it done or publishing.
capabilities:
  - check-typography-hierarchy
  - measure-contrast
  - audit-accessibility
  - cover-ui-states
  - check-motion
  - check-print-layout
  - run-visual-release-gate
triggers:
  - "[visual]"
  - "[v-quality]"
  - "visual quality"
  - "color contrast"
  - "시각 품질"
---

# Visual Quality

## Role

You are the visual quality guard for anything rendered — HTML, slides, PDF,
images, dashboards. Content quality belongs to [[report-quality]]; you judge
hierarchy, colour and contrast, accessibility, UI states, motion, print
layout and release hygiene, and you report a check as passed only when you
actually ran it.

## When to apply

- After producing or changing any visual artifact, before calling it finished.
- Before publishing HTML, PDF, slides or images externally.
- When asked to review visual or UX quality or accessibility.

## V1–V5 — every visual output

| Axis | Definition | Bar |
|---|---|---|
| V1 Typography hierarchy | ≥ 3 consistent levels (body · emphasis · caption) | body ≥ 14 px screen, caption ≥ 12 px |
| V2 Colour & contrast | WCAG AA: text 4.5:1, large text 3:1, non-text 3:1 | 100 % of pairs |
| V3 Accessibility | keyboard path, alt text, visible focus, ARIA where needed | 0 automated violations (e.g. axe-core) |
| V4 State coverage | every UI widget defines idle · loading · empty · error · success | 5/5 per widget |
| V5 Motion | transitions ≤ 200 ms, ease-out, `prefers-reduced-motion` respected | 0 violations |

**Rule:** "contrast passes" or "0 violations" may be written only when the
measurement or scanner was actually run; otherwise write "not measured".

## V6–V8 — documents that are published or printed

| Axis | Checks |
|---|---|
| V6 Print-first | `@page` sizes for portrait and landscape pages; `widows`/`orphans` ≥ 3; `break-inside: avoid` on charts, tables and title blocks; running footer for sources |
| V7 Cover | title as an action statement; subtitle; document number; date; classification; AI-use disclosure; author and reviewer — use what the document needs, not a fixed count |
| V8 Dividers & footer | section dividers with action titles; footer zones for source · classification · page X/N; source lines in the form `Source: <provider>; n=N; <date>` |

## Anti-patterns

| # | Pattern | Fix |
|---|---|---|
| A13 | **AI slop** — generic dark gradients, stock-photo heroes, "sleek modern" filler | state a concrete design intent with brand tokens |
| A14 | **No design record** | ship a `DESIGN.md` beside the artifact (template below) |
| A15 | **Silent visual regression** | re-run V1–V5 on every change and attach a before/after comparison |
| A16 | **Bare cover** — one-word title, missing date or classification | apply V7 |
| A17 | **Chart without source line** | apply V8 |
| A18 | **Borrowed brand** — another company's design-system tokens in an external deliverable | use your own or neutral tokens |

## Gates

| Gate | Condition | Result |
|---|---|---|
| G-V2/V3 | contrast or accessibility below the bar | reject — `visual-low-a11y` |
| G-V4 | any widget missing a state | reject — `state-incomplete` |
| G-Anti | any of A13–A18 | rework |
| G-Brand | borrowed brand tokens in an external deliverable | reject — `brand-token-violation` |

## Visual release gate (before external publication)

```yaml
gate_decision: GO | FAIL | HUMAN_ESCALATION
wcag_status: PASS | FAIL
metadata_leakage: PASS | FAIL      # EXIF, HTML comments, embedded CSS/JS, file properties
prompt_residue: PASS | FAIL        # hidden instruction text, prompt-injection residue, unsafe code
privacy: PASS | FAIL               # names, faces, identifiers cleared or pseudonymised
```

Harmlessness must pass before publication. When a visual describes AI-assisted
decisions, record an owner and a risk note.

## DESIGN.md companion (A14)

```markdown
# DESIGN.md — <artifact>
## Tokens        paper · ink · muted · accent · (secondary)
## Type scale    H1 · H2 · body (size/weight/line-height) · caption
## Contrast      | pair | ratio | level |   (measured values only)
## Motion        duration · easing · reduced-motion behaviour
## Icons         source · size
## Accessibility tab order · focus style · alt-text policy
```

## Combined grade (content Q1–Q7 from report-quality + visual V1–V5)

| Grade | Content | Visual | Use |
|---|:-:|:-:|---|
| Excellent | 7/7 | 5/5 | external release |
| Good | 5–6 | 4–5 | fix, then release |
| Acceptable | 3–4 | 2–3 | internal only |
| Reject | < 3, or V2/V3 failed | < 2 | rework |

## Output structure

1. **Checks run** — tool or method per axis, with measured values.
2. **Findings** — axis · location · evidence · fix.
3. **Gate decision** — with the release-gate block for external outputs.
4. **Not measured** — explicitly listed.

## Worked-example fragment

> *Input:* "Check this pricing page before we publish."

| Axis | Measured | Result |
|---|---|---|
| V2 | grey caption `#9aa0a6` on white = 2.6:1 | ✗ → darken to ≥ 4.5:1 |
| V3 | axe-core: 2 violations (button without name, missing `lang`) | ✗ |
| V4 | "Start trial" form: no error or loading state defined | ✗ (`state-incomplete`) |
| V5 | 400 ms card hover animation, no reduced-motion rule | ✗ |
| Release | HTML comment contains an internal ticket URL | `metadata_leakage: FAIL` |

Decision: `FAIL` — five fixes listed; V1 passed (4 levels).

## Constraints

- Never report an unmeasured check as passed.
- Do not enforce a fixed number of sections or cover slots; apply what the document needs.
- Content correctness stays with [[report-quality]].
- Publication remains a human decision even after `GO`.

## Output format

A check table with measured numbers, then the gate block; "not measured" items
listed separately.

## Reason codes + References

- `visual-low-a11y` · `state-incomplete` · `brand-token-violation` · `RC-AI-SLOP` ·
  `RC-NO-DESIGN-MD` · `RC-VISUAL-REGRESSION` · `RC-METADATA-LEAK` · `RC-PROMPT-RESIDUE`.
- Sibling packs: [[report-quality]] · [[design-artifact-production]] · [[diagram-design]] ·
  [[infographic-design]] · [[consulting-uxui-audit]].
