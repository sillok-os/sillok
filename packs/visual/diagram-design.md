---
id: diagram-design
title: Diagram Design — editorial diagrams with one accent, hairlines and a 4-unit grid
category: workflow
sub_category: visual
license: Apache-2.0
status: starter
version: 0.1.0
references:
  - "cathrynlavery/diagram-design — editorial diagram skill (type catalogue and style philosophy)"
  - "W3C — WCAG 2.2 contrast (1.4.3) and non-text contrast (1.4.11)"
  - "Edward Tufte — The Visual Display of Quantitative Information (data-ink)"
  - "SVG 2 — accessible <title> and <desc>"
top10_features: ["#3 typed registry"]

# agentskills.io v0.9 capability discovery (additive)
name: diagram-design
description: Choose the right diagram type and render it as self-contained HTML + SVG with tokens, one accent and WCAG AA.
capabilities:
  - select-diagram-type
  - apply-design-tokens
  - render-inline-svg
  - check-grid-and-contrast
  - keep-data-geometry-exact
triggers:
  - "[diagram]"
  - "architecture diagram"
  - "flowchart"
  - "sequence diagram"
  - "다이어그램"
---

# Diagram Design

## Role

You draw technical and product diagrams of editorial quality: the right type
for what is happening, minimal ink, one accent colour, 1 px hairlines, a
4-unit grid and AA contrast, delivered as a single self-contained HTML file
with inline SVG. You prefer deleting an element to adding one.

## When to apply

- Architecture, flow, sequence, state, ER, swimlane, timeline, hierarchy, layer or set diagrams.
- Replacing a hard-to-maintain Mermaid or slide drawing with clean SVG.
- Small quantitative charts that must match the same visual system.

Colourful information posters and data-viz infographics → [[infographic-design]].
Visual QA of the result → [[visual-quality]].

## 1. Select the type in two steps

**Step 1 — what is happening?** Name the behaviour before the shape:
bottleneck, trust boundary, hand-off, feedback loop, compensation/rollback,
fan-out/fan-in, state change. The behaviour decides what must be emphasised.

**Step 2 — which type shows it?**

| Type | Use when |
|---|---|
| architecture | components and connections; planes, zones, tiers |
| flowchart | decision logic with branches |
| sequence | messages between actors over time |
| state | finite states and transitions |
| er | entities, fields, cardinality |
| timeline | events along one axis |
| swimlane | cross-functional flow across actor lanes |
| quadrant / 2×2 | two-axis positioning of options |
| nested | hierarchy by containment |
| tree | parent → children branching |
| layers | stacked abstractions |
| venn | set overlap |
| pyramid | what compounds from bottom to top |
| bar · line · scatter · gantt | measured comparison, trend, correlation, schedule |
| process · loop · data-flow | operating cycles and data movement |

Analytical consulting charts (waterfall, Marimekko, growth-share) belong to a
report or infographic pack; this pack covers structure first.

## 2. Tokens, not hex

Resolve colours as semantic roles and emit them as CSS variables:

| Role | Purpose | Example fallback |
|---|---|---|
| `--paper` | background | `#faf7f5` |
| `--ink` | text and primary strokes | `#1e293b` |
| `--muted` | secondary labels | `#475569` |
| `--accent` | the single emphasis colour | `#1e3a5f` |
| `--accent-wash` | accent tint for fills | `rgba(30,58,95,.06)` |
| `--hairline` | 1 px rules and borders | `rgba(30,41,59,.22)` |

Check every pair against WCAG AA: text ≥ 4.5:1, large text and strokes ≥ 3:1.
Many attractive defaults fail on light paper — e.g. slate `#64748b` on `#faf7f5` is 4.46:1, just under AA — measure, don't assume.
For Korean, Japanese or Chinese labels, put a CJK-capable font in the stack
(display serifs often have no Hangul glyphs).

## 3. Style rules

1. **One accent per diagram.** Two accents → two diagrams.
2. **1 px hairlines**; no shadows, gradients or decorative rounding.
3. **4-unit grid** for layout coordinates (`x`, `y`, `x1`…, `cx`, `cy`, `translate`).
   Exception: in data charts, bar lengths and point positions use the exact values;
   only axes and labels snap to the grid.
4. Never mix units (percent vs count) in one bar group.
5. Hex values only inside the `<style>` block that defines variables.
6. Self-contained output: no external scripts or images; web fonts allowed.
7. Accessible: `<title>` and `<desc>` on the SVG, and a text alternative for dense diagrams.

## 4. Procedure

1. Decide behaviour → type.
2. Load the project's tokens (or the fallbacks above) and check contrast.
3. Lay out on the grid; label with the field's own terms.
4. Emit one `.html` file with inline SVG.
5. Run three checks: **structure** (no external assets, title/desc present),
   **geometry** (grid alignment, no overlaps, exact data values), **palette**
   (no stray hex, one accent, AA pairs).
6. Open the file and look at it at the size it will be used.

## Quality contract

| Check | Pass |
|---|---|
| Hard-coded hex outside `<style>` | 0 |
| Layout coordinates on the 4-unit grid | 100 % (data geometry exempt) |
| Shadows / gradients | 0 |
| ink/paper and accent/paper contrast | ≥ 4.5:1 |
| Accent colours used | exactly 1 |
| External JS or images | 0 |

## Output structure

1. **Type decision** — behaviour, chosen type, why not the runner-up.
2. **Token table** — roles, values, contrast ratios.
3. **The file** — path to the self-contained HTML.
4. **Check results** — structure · geometry · palette, with numbers.

## Worked-example fragment

> *Input:* "Draw how a support ticket moves between the customer, the bot, an agent and engineering."

- Behaviour: hand-offs across actors, with one escalation loop → **swimlane**
  (a sequence diagram would hide the ownership of each step).
- Lanes: customer · bot · agent · engineering; the escalation edge is the only
  element in `--accent`; everything else is `--ink` on `--paper` with `--hairline` lanes.
- Checks: 0 stray hex · 112/112 coordinates on the grid · ink/paper 13.7:1,
  accent/paper 10.8:1 · muted/paper 7.1:1 · 1 accent.

## Constraints

- Do not fetch a client's website to extract brand colours without explicit authorisation.
- Do not edit a vendored upstream diagram skill in place; customise through tokens.
- Do not round data values to fit the grid.
- Do not claim AA without computing the ratios.

## Output format

A single self-contained `.html` with inline SVG plus a short check report. An
optional footer line may state the philosophy: `ONE ACCENT · 1PX HAIRLINES · 4-UNIT GRID · NO SHADOWS`.

## Reason codes + References

- `RC-TWO-ACCENTS` · `RC-HARDCODED-HEX` · `RC-OFF-GRID` · `RC-LOW-CONTRAST` ·
  `RC-DATA-ROUNDED` · `RC-MIXED-UNITS` · `RC-NO-CJK-FONT`.
- Sibling packs: [[infographic-design]] · [[visual-quality]] · [[design-artifact-production]] · [[report-quality]].
