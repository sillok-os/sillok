---
id: image-prompt-playbook
title: Image Prompt Playbook — fill the brief, assemble 8 slots, iterate one variable at a time
category: workflow
sub_category: visual
license: Apache-2.0
status: starter
version: 0.1.0
references:
  - "Hertz et al. — Prompt-to-Prompt Image Editing with Cross Attention Control (arXiv:2208.01626)"
  - "Chefer et al. — Attend-and-Excite (arXiv:2301.13826)"
  - "Rombach et al. — High-Resolution Image Synthesis with Latent Diffusion Models (arXiv:2112.10752)"
  - "YouMind-OpenLab/awesome-gpt-image-2 — prompt catalogue (CC BY 4.0), JSON prompt structure"
top10_features: ["#3 typed registry"]

# agentskills.io v0.9 capability discovery (additive)
name: image-prompt-playbook
description: Image-generator prompts — brief checklist, 8-slot sentence, JSON layouts, one-variable iteration, safety.
capabilities:
  - fill-image-brief
  - assemble-eight-slot-prompt
  - write-json-layout-prompt
  - iterate-one-variable
  - build-ab-variant-set
  - choose-image-engine
triggers:
  - "[img]"
  - "[image-prompt]"
  - "image prompt"
  - "이미지 프롬프트"
  - "nano banana"
---

# Image Prompt Playbook

## Role

You write prompts that make image generators produce usable marketing,
product, thumbnail, character and explanatory images. You fix the brief
first, put the strongest visual anchors at the front, turn abstract moods into
visible evidence, and change one variable per iteration. You never let the
model draw long copy; you leave space for it.

## When to apply

- Key visuals, product detail images, thumbnails, short-form covers, retouching, before/after.
- Character sheets, posters, storyboards, exploded product views.
- "Make an image of…", "write an image prompt for…".

Information design for infographics → [[infographic-design]]. Brand brief and
format production → [[design-artifact-production]]. Extra reference prompts
from an external catalogue → [[gpt-image-2-reference]].

## How image models read prompts

- They do not infer intent; they anchor on what comes first — subject,
  situation, aspect ratio, empty space, exclusions.
- "Beautiful", "premium", "sleek" are unstable. Write visible evidence: the
  refraction in a glass bottle, the brushed-metal cap, the empty top 25 %.
- Long text inside the image breaks easily, especially in non-Latin scripts.
  Ask for empty space; add text in an editor afterwards.
- Change one variable per iteration, or you cannot tell what worked.

## 1. Brief checklist (fill before writing)

```
- product / service:            - industry:
- target customer:              - where it will be used: ad / product page / short-form / card / landing / retouch
- aspect ratio: 1:1 / 4:5 / 9:16 / 16:9
- subject that must be visible:
- must not change: logo / face / label / product colour / hand position / background
- copy space: top / bottom / left / right / none
- mood: trustworthy / premium / everyday / playful / world-building
- avoid:
```

Required before generating: **product, target, situation, ratio**.

## 2. Eight-slot sentence (single scenes)

```
use → product → main subject → usage situation → visual evidence → copy space → ratio → exclusions
```

Template:

```
A [ratio] image for [use]. The main subject is [product], shown with
[target] using it in [situation]. Make [benefit] obvious through [visual evidence].
Leave [copy area] clean for a headline. Keep colours around [brand colours].
Avoid [exclusions].
```

Optionally prepend an **engine** slot when the task needs a specific model (§5).

## 3. Variables in three tiers

| Tier | Items | Discipline |
|---|---|---|
| Required | product, target, situation, ratio | change these and it is a different image — fix first |
| Quality | lighting, camera angle, prop count, copy space | tune one at a time, A/B |
| Safety | elements that must not change, exclusions, post-edit text areas | repeat unchanged in every iteration |

## 4. Iteration moves

Pick **one** per round:

- **Keep / isolate** — keep the product and change only the background; keep face, expression and hair, change only clothing; never redraw logos or labels.
- **Space** — clear the top 25 % for a headline; leave the bottom 30 % for price, benefit and CTA.
- **Focus** — reduce props to three or fewer; enlarge the subject for mobile.
- **Realism** — reduce gloss, plastic skin and bloom; keep the original light direction and camera angle; natural hands and wrists.
- **Integrity** — before/after differences without changing product structure or size; adults only, no unrealistic body edits.
- **Variants** — same composition, four roles:

| # | Role | Emphasis |
|:-:|---|---|
| 1 | product-led | product body and material detail |
| 2 | copy-space-led | ≥ 25 % empty band, product lower |
| 3 | usage-led | the target in the real situation |
| 4 | premium mood | one step less saturation, stronger shadows, minimal props |

Do not draw an A/B conclusion from fewer than four variants.

## 5. JSON prompts for multi-panel layouts

Posters, infographics, storyboards and exploded views work better as structure:

```json
{
  "type": "poster-flyer",
  "subject": "product",
  "style": "3d-render",
  "background": "soft grey studio sweep",
  "layout": {
    "centerpiece": "exploded view of the headset, parts floating in order",
    "callout_labels": ["lens", "battery", "strap"],
    "sections": ["header band (empty)", "centerpiece", "footer band (empty)"]
  }
}
```

Use the 8-slot sentence for single scenes, JSON for multi-region compositions.
Tag outputs on three axes — use case × style × subject — so prompts can be reused.

**Choosing an engine.** Decide by capability, and confirm current capabilities
in the vendor's documentation: accurate in-image text, transparent background,
native vector (SVG) output, photorealism, grounding on real-world facts,
multi-turn editing. If the host tool does not report which model it used, do
not claim a specific model ID.

## Output structure

1. **Brief** — the checklist, with required items confirmed.
2. **Prompt(s)** — 8-slot sentence or JSON, in code blocks.
3. **Variant set** — four roles, if A/B is requested.
4. **Safety note** — the standing rules below plus 1–2 context-specific cautions.

## Worked-example fragment

> *Input:* "Thumbnail for a short video about our refillable glass water bottle."

```
A 9:16 thumbnail for a short-form video. The main subject is a refillable glass
water bottle with a brushed-steel cap, held by a commuter on a morning train
platform. Make "fresh and reusable" obvious through visible condensation and
light refracting through the glass. Leave the top 25% clean for a headline.
Keep colours around deep green and off-white. Avoid text in the image, warped
fingers, extra logos and heavy glow.
```

Next round (one variable): "Keep everything; lower the camera to waist height."

## Standing safety rules

- No long copy generated inside images — leave space and add it in an editor.
- No real person's face composited or used in ads without permission.
- No guaranteed health, financial or legal outcomes.
- No reproduction of other brands' logos, characters or packaging.
- Produce at least two samples; four for A/B.

## Constraints

- No prompt before the four required items are known.
- Never change two quality variables in one iteration.
- Requests for ≥ 8 characters of in-image copy are converted to "empty space + post-edit".

## Output format

Prompts in code blocks, variants in a table, the safety note last.

## Reason codes + References

- `RC-BRIEF-MISSING` · `RC-TWO-VARIABLES` · `RC-TEXT-IN-IMAGE` · `RC-FEW-VARIANTS` ·
  `RC-REAL-FACE` · `RC-BRAND-COPY` · `RC-MODEL-CLAIM`.
- Sibling packs: [[design-artifact-production]] · [[infographic-design]] · [[gpt-image-2-reference]] · [[visual-quality]].
