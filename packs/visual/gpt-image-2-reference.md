---
id: gpt-image-2-reference
title: GPT-Image-2 Reference — external prompt catalogue as a cited, adapted fallback
category: workflow
sub_category: visual
license: Apache-2.0
status: starter
version: 0.1.0
references:
  - "YouMind-OpenLab/awesome-gpt-image-2 — community prompt catalogue (CC BY 4.0)"
  - "Creative Commons — Attribution 4.0 International (CC BY 4.0)"
top10_features: ["#3 typed registry"]

# agentskills.io v0.9 capability discovery (additive)
name: gpt-image-2-reference
description: Fallback to an external image-prompt catalogue — fetch a few, adapt them, keep attribution and taxonomy tags.
capabilities:
  - search-external-prompt-catalogue
  - adapt-reference-prompt
  - preserve-cc-by-attribution
  - tag-prompt-taxonomy
triggers:
  - "[gpt-image-2]"
  - "[awesome-gpt-image-2]"
  - "awesome-gpt-image-2"
  - "reference prompts"
  - "참고 프롬프트"
---

# GPT-Image-2 Reference (external catalogue fallback)

## Role

You are a **fallback** for [[image-prompt-playbook]]. When local prompts and
the playbook's own patterns are not enough, you consult a public, licensed
prompt catalogue, take a handful of relevant prompts, **adapt** them to the
user's brief, and keep the attribution. This pack is a reference catalogue
only — it does not choose or call an image API.

## When to apply

Low precedence; activate only when:

1. explicitly invoked (`[gpt-image-2]`, `[awesome-gpt-image-2]`);
2. the request names a specific catalogue category (e-commerce main image,
   video thumbnail, exploded-view poster, product marketing); or
3. the playbook has been applied and the user asks for more reference prompts.

Infographic requests go to [[infographic-design]] first.

## Procedure

1. **Local first.** Apply [[image-prompt-playbook]] (checklist → 8-slot or JSON).
   If the result is good enough, use the catalogue only as inspiration and do
   not fetch.
2. **Fetch narrowly.** Open the catalogue page for the matching category and
   take at most five candidate prompts. Cache what you fetched with its date.
3. **Select.** Keep the one or two candidates that fit the user's product,
   audience and ratio.
4. **Adapt, don't copy.** Rebuild them in the playbook's 8-slot or JSON form;
   map catalogue parameter slots (e.g. `{argument name="hair style" default="…"}`)
   to the playbook's required / quality / safety variables.
5. **Tag.** Record use case × style × subject (and language).
6. **Attribute.** Keep source, author and licence with the prompt.

## Taxonomy (three axes)

| Axis | Examples |
|---|---|
| Use case | profile avatar · social post · infographic/edu visual · video thumbnail · comic/storyboard · product marketing · e-commerce main image · game asset · poster/flyer · app/web design |
| Style | photography · cinematic still · anime/manga · illustration · line art · 3D render · isometric · pixel art · oil painting · watercolour · retro |
| Subject | portrait · character · group · product · food & drink · fashion item · animal · vehicle · architecture/interior · landscape · cityscape · diagram/chart |

Use the catalogue's own category names; do not invent new categories silently.

## Provenance record

```yaml
imported_from: "awesome-gpt-image-2/<page>#<anchor>"
fetched: "<YYYY-MM-DD>"
original_author: "<as credited in the catalogue>"
license: "CC-BY-4.0"
taxonomy: { use_case: poster-flyer, style: 3d-render, subject: product, language: en }
adapted: true
```

## Output structure

1. **Why the fallback was used** — what the local playbook lacked.
2. **Sources** — up to five candidates with URLs and fetch date.
3. **Adapted prompt(s)** — in playbook form.
4. **Provenance record** — per adapted prompt.

## Worked-example fragment

> *Input:* "[gpt-image-2] give me reference prompts for an exploded-view poster of our wireless earbuds."

- Local playbook JSON draft existed but lacked a convincing layout for part callouts.
- Fetched 4 candidates from the catalogue's poster/product category (dated); kept 1.
- Adapted: centerpiece = earbuds and case separated along one vertical axis;
  callout labels = driver · battery · charging contacts; header and footer bands left empty.
- Provenance: catalogue page + original author + CC BY 4.0, taxonomy
  `poster-flyer × 3d-render × product`.

## Constraints

- **No bulk scraping** — never import the whole catalogue; take only what the task needs.
- **No infringing prompts** — no protected characters, celebrities or copyrighted slogans.
- **No NSFW or harmful content.**
- **Never hide the fallback** — say that the external catalogue was consulted.
- Licence terms apply: CC BY 4.0 requires attribution.

## Output format

Adapted prompts in code blocks, each followed by its provenance record.

## Reason codes + References

- `RC-BULK-IMPORT` · `RC-NO-ATTRIBUTION` · `RC-VERBATIM-COPY` · `RC-UNTAGGED` · `RC-HIDDEN-FALLBACK`.
- Sibling packs: [[image-prompt-playbook]] · [[infographic-design]] · [[design-artifact-production]].
