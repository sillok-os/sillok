---
id: infographic-design
title: Infographic Design Pack — 10 Pattern × 13-Slot × EAA/IIB Self-Eval
category: output-style
sub_category: visual
license: Apache-2.0
license_atoms: CC-BY-4.0
status: starter
version: 0.1.0a1
references:
  - "Tufte — The Visual Display of Quantitative Information (2001)"
  - "Cairo — The Functional Art / 5-Quality framework"
  - "Information is Beautiful Awards — 8-axis rubric"
  - "EU European Accessibility Act (2025-06-28)"
  - "WCAG 2.2 AA — Color contrast and accessibility"
top10_features: ["#3 typed registry", "#4 governance gate"]

# agentskills.io v0.9 capability discovery (additive — docs/architecture/frontmatter-compatibility.md)
name: infographic-design
description: Infographic generation — 10 pattern × 13-slot × Tufte/Cairo/IIB/EAA self-eval gates.
capabilities:
  - select-pattern-from-10
  - compose-13-slot-prompt
  - run-eaa-5-gate-accessibility
  - score-iib-8-axis
triggers:
  - "[infographic]"
  - "infographic"
  - "정보 시각화"
  - "데이터 시각화"
  - "인포 디자인"
  - "data viz"
---

# Infographic Design Pack

> **목적**: 인포그래픽(정보 시각화 산출물) 생성 워크플로우를 표준화. Tufte/Cairo/IIB/EAA-grade 산출물을 다중 image-gen 백엔드(GPT-Image-2 / Gemini / Recraft / Flux)로 생성하고 자가 평가 게이트를 통과시킨다.
>
> **차이점 (vs adjacent)**:
> - Single-scene marketing image → use a single-image prompt pack
> - Editorial diagram (architecture/flow/sequence) → use a diagram pack
> - **This pack** → information visualization (10 pattern, 13-slot, data honesty + accessibility hard gate)

## 1. Scope

| Concern | Pack |
|-------|-------|
| **Infographic (10 pattern + 13-slot)** | **This pack** |
| Single photo/ad image | Single-image prompt pack |
| Tech/product/org diagram | Diagram pack |
| External delivery hardening | External-delivery hardening pack |

This pack focuses on **data information visualization**. "Charts cover ≥60% of canvas" or "multi-panel + label + icon" outputs belong here.

## 2. Trigger signals

- **Explicit**: `[infographic]`, `[infogr]`, `[info-design]`, `[data-viz-infographic]`
- **Contains (Korean)**: `인포그래픽`, `정보 시각화`, `데이터 시각화`, `인포 디자인`, `매거진 인포`, `브로셔 인포`, `카드뉴스 인포`
- **Contains (English)**: `infographic`, `data infographic`, `flat infographic`, `isometric infographic`, `comparison infographic`, `pyramid infographic`, `step-by-step infographic`, `timeline infographic`
- **Co-occurrence**: image-prompt trigger + user mentions "차트", "단계별", "비교", "통계", "%", "데이터" → route here

## 3. 13-Slot assembly

```
[1 ENGINE] gpt-image-2 | gemini-3-pro | recraft-v3 (icon SVG) | flux-1.1-pro
[2 destination] magazine / PPT slide / social card / dashboard / printed brochure
[3 topic] <text>
[4 subject type] data / process / comparison / hierarchy / map / hero-stat / timeline
[5 usage] internal draft / executive review / external delivery / public social
[6 visual evidence] 3D effects / shadows / gradients allowed?
[7 copy margin] top / bottom / left rail / none
[8 ratio] 16:9 (dashboard) / 9:16 (mobile) / 1:1 (social) / 4:5 (Instagram) / 2:3 (magazine)
[9 data_density] low (1 stat) / medium (3-5 stats) / high (8+ stats)
[10 icon_set] minimalist line 2px / flat filled / 3D iso / hand-drawn / pixel art
[11 chart_type] bar / donut / line / funnel / Venn 3-circle / radial / heatmap / none
[12 hierarchy_pattern] flat / linear flow / radial / pyramid / nested / comparison-split / timeline-axis
[13 negative] no chartjunk, no scrambled text, no 3D shadow, no gradient fill, no decorative gridline, no fake data
```

### Pattern → slot auto-mapping (router cheatsheet)

| Pattern | data_density | icon_set | chart_type | hierarchy_pattern | Recommended ENGINE |
|---|---|---|---|---|---|
| 1 Flat | medium | flat filled | none/bar | flat | gpt-image-2 |
| 2 Isometric | medium | iso 3D | none | nested | gpt-image-2 |
| 3 Data-viz | high | flat | bar+donut+line | flat | gpt-image-2 |
| 4 Process | medium | line 2px | none | linear flow | gpt-image-2 |
| 5 Comparison | medium | flat filled | none | comparison-split | gpt-image-2 |
| 6 Icon grid | low | line 2px | none | flat | recraft-v3 (SVG) |
| 7 Hero-stat | low (1) | none | none | flat | gpt-image-2 |
| 8 Timeline | medium | flat filled | none | timeline-axis | gpt-image-2 |
| 9 Map | high | flat pins | heatmap | flat | **gemini-3-pro (Search grounding)** |
| 10 Pyramid | low-medium | none | none | pyramid | gpt-image-2 |

## 4. 10 Prompt Pattern Catalog

Each pattern has **(a) definition (b) appropriate use case (c) per-tool template (d) negative prompt (e) aspect ratio (f) safe limits**.

### 4.1 Flat Design

**Definition**: 2D geometric shapes + solid color + zero gradient/shadow vector illustration.
**Use case**: B2B reports, magazines, education, card-news.

```
GPT-Image-2:
"Modern flat vector infographic on '<TOPIC>'. Layout: landscape 16:9, 4-section grid.
Style: minimalist 2D vector, solid color blocks, no gradients, no shadows.
Palette: navy #1F2937 + coral #F97316 + cream #FFFBEB (3-color discipline).
Typography: bold sans-serif headline + thin body, all text in straight quotes."
```

- **Negative**: `no photorealism, no shadows, no gradients, no chart-junk, no scrambled text`
- **Aspect**: 16:9 (magazine), 9:16 (Instagram reels), 1:1 (thumbnail)
- **Limits**: outside GPT-Image-2, Korean text 5+ chars often broken. Flux outputs ALL CAPS literally.

### 4.2 Isometric 3D

**Definition**: 30°/120° axonometric projection, 3-face exposure, no vanishing point.
**Use case**: cities · workflows · architecture · team structure.

```
GPT-Image-2:
"Isometric 3D infographic of '<TOPIC>'. Camera: 30-degree axonometric, parallel lines,
no vanishing point. Layout: vertical 9:16, 5 floating tile platforms ascending diagonally.
Palette: muted teal + gold accent on neutral gray. Soft key light + gentle rim light."
```

- **Negative**: `no perspective distortion, no vanishing point, no fisheye, no top-down 2D`
- **Aspect**: 9:16 (staircase progression), 1:1 (city layout)

### 4.3 Data Visualization-Heavy

**Definition**: bar/pie/line charts cover 60%+ of canvas (dashboard style).
**Use case**: quarterly reports, KPI dashboards, market share.

```
GPT-Image-2:
"Modern data dashboard infographic '<TITLE>'. Layout: landscape 16:9, 4 floating cards.
Card 1: 3D bar chart with 5 bars. Card 2: glossy donut chart with 3 segments.
Card 3: smooth line graph with 12 data points. Card 4: KPI tile with single hero number.
All numbers and axis labels in straight quotes. Palette: deep coffee brown + electric blue + cream."
```

- **Negative**: `no chart-junk, no 3D extrusion shadows, no overlapping labels, no fake data`
- **Limits**: **No tool plots accurate data** — visual containers only; overlay real data via Datawrapper / Flourish / Excel.

### 4.4 Step-by-Step Process

**Definition**: numbered icons + arrow connectors, N-step flow (vertical/horizontal/S-curve).
**Use case**: SOPs, onboarding, methodology guides.

- **Safe limit**: **5 steps**. 7+ commonly produces label collisions; split.

### 4.5 Comparison Split-Screen

**Definition**: 2-column symmetric + central divider + contrasting palette for A vs B.
**Use case**: feature comparison, before/after, competitor analysis.

- **Limit**: pure side-by-side handles 2-way only. 3+ ways → grid (2×2, 3×2).

### 4.6 Icon-Heavy Grid

**Definition**: 3×3 or 3×4 grid, consistent stroke icons + short labels.
**Use case**: quick fact sheets, feature summaries, checklists.

- **Engine**: Recraft v3 recommended (SVG output → post-process stroke uniformity).

### 4.7 Hero-Stat (Single Big Number)

**Definition**: single massive number (5x scale) + short supporting context.
**Use case**: ad hero, single keynote slide, KPI announcement.

- **Limit**: **3 digits max**. 4+ digit accuracy drops across all models.

### 4.8 Timeline (horizontal/vertical)

**Definition**: horizontal/vertical axis + year markers + milestone illustration.
**Use case**: company history, product roadmap, evolution.

- **Limit**: 8+ milestones cause label collision — go vertical or split.

### 4.9 Map-Based World/Country

**Definition**: world/country map + data points + color coding.
**Use case**: global market, regional stats, travel.

- **Engine**: Gemini 3 Pro Image (Search grounding) for current data — GPT-Image-2 also struggles with up-to-date political boundaries. Use Mapbox/D3 for accuracy.

### 4.10 Pyramid / Hierarchy

**Definition**: 4-5 level triangle + base-to-apex hierarchy + color gradient.
**Use case**: Maslow's hierarchy, marketing funnel, organizational levels.

- **Limit**: **5-level safe ceiling**. 6+ degrades base-label readability.

## 5. Tool-handoff matrix (12-row use-case mapping)

| Use case | 1st choice | 2nd choice |
|----------|---------|---------|
| Concept-comparison drafts (10 in 1 batch) | Multi-image batch tool | Single-image gen |
| Single high-fidelity final | gpt-image-2 (single) | Adobe Firefly |
| Real-time data (Map / Trend) | Gemini 3 Pro Image | gpt-image-2 |
| Icon-grid SVG | Recraft v3 | Figma + AI |
| Series brand kit (≥5 same-brand) | Canva | Visme |
| Accurate charts (data journalism) | Datawrapper | Flourish |
| Sankey / treemap | Infogram | Tableau |
| Interactive scrollytelling | Flourish | D3.js |
| 1-shot draft (text → diagram) | Napkin AI | Multi-image batch |
| Design-system component | Figma + AI | Adobe XD |
| License-sensitive (finance/medical/gov) | Adobe Firefly (commercially safe) | gpt-image-2 + license check |

## 6. EAA + IIB self-eval hard gate

### 6.1 EAA 2025-06-28 5-gate accessibility (external delivery hard gate)

EU market digital outputs mandated (existing services 2030-06-28 grace).

- [ ] **Alt-text** — descriptive alt-text ≤125 chars (Korean ≤200 chars) for PNG/SVG outputs
- [ ] **Data table sibling** — complex infographics ship a plain HTML/markdown table sibling
- [ ] **Heading hierarchy** — h1×1 + h2/h3 hierarchy maintained (when embedded in pages)
- [ ] **WCAG 2.2 AA contrast** — text-background ≥4.5:1 (large ≥3:1)
- [ ] **SVG `<title>/<desc>` + role='img'** — mandatory for SVG outputs

### 6.2 IIB 8-axis self-score (pre-output)

Each scored 1-5; **average ≥4.0 + Accessibility ≥4 hard gate**.

| Axis | Question |
|------|---------|
| Impact | Does the output drive actual decision/action? |
| Engagement | Does the eye linger and read through? |
| Clarity | Can the core message be extracted in one sentence? |
| Innovation | New angle / combination / discovery present? |
| **Inclusivity** | Diverse readers (age / culture / language) considered? |
| **Accessibility** | All EAA 5 gates met (hard gate) |
| Effectiveness | Data honesty + visual clarity |
| Beauty | Typography · color · composition consistency |

### 6.3 Cairo 5-quality sequential gate

Truthful → Functional → Beautiful → Insightful → Enlightening order. **If Truthful (1) fails, abort output**.

- [ ] **Truthful**: source URL + collection date in footer; lie factor 0.95-1.05 verified
- [ ] **Functional**: one page = one take-away; charts ≤5
- [ ] **Beautiful**: 2-tier typography; single accent; padding ≥10%
- [ ] **Insightful**: not mere reporting — at least one new finding
- [ ] **Enlightening**: social/practical value explicit

### 6.4 Tufte data-ink self-check

- [ ] data-ink ratio ≥70%
- [ ] gridline 1px hairline, single tier only
- [ ] 3D shadow / gradient fill / decorative gridline removed
- [ ] redundant icons removed (Isotype overuse forbidden)

## 7. Output contracts

```yaml
output_contracts:
  - prompt-template          # 13-slot filled prompt
  - pattern-rationale        # which of 10 patterns + why
  - engine-selection         # gpt-image-2 / gemini / recraft / flux + rationale
  - negative-prompt-set      # standard negative prompt by pattern
  - aspect-ratio-recommendation
  - post-edit-todo           # data charts require post-editing
  - eaa-self-eval            # 5-gate accessibility (hard gate for external)
  - iib-8axis-score          # 8 axes + average + accessibility score
  - cairo-5quality-pass      # Truthful pass/fail (abort on fail)
  - source-citation          # source URL + collection date for external data
```

### Response length by trigger

- **Quick 1-shot**: 13-slot prompt + 1 ENGINE + key negatives (≤150 words)
- **Deep pattern comparison**: 3-5 patterns + tool selection (300-500 words)
- **External delivery output**: above + EAA 5-gate self-eval + IIB 8-axis + Cairo 5-quality (≥600 words)

## 8. Quality guards

| Gate | Rule |
|------|------|
| **G1 Text quality** | All labels/numbers/titles in straight quotes. No ALL CAPS input (especially Flux). Korean 5+ chars → force gpt-image-2 routing. |
| **G2 Negative prompt** | ≥5 negative-prompt items per pattern (chart-junk, scrambled text, 3D shadow, gradient fill, decorative gridline). |
| **G3 Data accuracy** | No tool plots accurate data — containers only. Mandatory post-edit notice (Datawrapper/Excel/Flourish). |
| **G4 Safe ceiling** | 5-step process / 5-level pyramid / 7-point timeline / 9-icon grid safe limits. Beyond → split. |
| **G5 Korean routing** | Korean 5+ char labels → force gpt-image-2 (Flux/MJ/DALL-E 3 break Korean 5+ chars). |
