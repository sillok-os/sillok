# Recipe — Decide what's reusable with `yeonryun`

> Score a research / closeout / retro markdown for reusability. Decide
> whether it should stay in repo, be absorbed locally, or be promoted
> to a shared vault as atomic notes.

## When to use

- You finished a piece of work and want to know what (if anything)
  should graduate into shared knowledge.
- You're sweeping a folder of past results and want a triage report
  before manual review.
- You want auto-extraction of one representative atom per source — the
  "promote a single best-fit atom" path that avoids signal/noise
  degradation in the receiving vault.

## CLI — score one file

```bash
python -m sillok.yeonryun.disposition research/2026-04-26-pricing.md

# Output:
# # Vault Disposition Report
# **date**: 2026-04-26 14:33
# **files scanned**: 1
#
# ## Summary
# - cross-repo-reusable: 1
# - local-reusable: 0
# - none: 0
#
# ## cross-repo-reusable (1)
# - **Pricing pattern** (score=14) — reusability score 14 (cross-repo>=6, local>=3)
```

## CLI — sweep a folder

```bash
python -m sillok.yeonryun.disposition --scan research/ --format json \
    | jq '[.[] | {file, disposition, score}]'
```

## CLI — auto-extract atomic notes

```bash
python -m sillok.yeonryun.disposition \
    --scan research/ \
    --auto-extract \
    --target-dir ~/Documents/my-vault/40_Knowledge/auto \
    --vault ~/Documents/my-vault \
    --source-repo sillok-os/sillok \
    --topic saas-pricing
```

By default a single representative atom is materialized per source
(highest priority among `pattern > decision > checklist > template >
case > prompt > insight`). Pass `--extract-all` only if you have an
explicit reason to fan out — fan-out tends to dilute the receiving
vault's signal.

## Python API

```python
from pathlib import Path
from sillok.yeonryun import (
    determine_disposition, process_file, scan_directory,
)

# Just decide, don't write anything
content = Path("research/2026-04-26-pricing.md").read_text()
result = determine_disposition(content, meta={})
print(result["disposition"])         # 'cross-repo-reusable'
print(result["score"])               # 14
print(result["extractable_atoms"])   # [{'knowledge_type': 'pattern', ...}, ...]

# Decide and write the representative atom
process_file(
    "research/2026-04-26-pricing.md",
    auto_extract=True,
    target_dir=Path("~/Documents/my-vault/40_Knowledge/auto").expanduser(),
    vault_root=Path("~/Documents/my-vault").expanduser(),
    source_repo="sillok-os/sillok",
    topic="saas-pricing",
)

# Sweep + report
results = scan_directory("research/")
for r in results:
    if r.get("disposition") == "cross-repo-reusable":
        print(r["file"], r["score"])
```

## Frontmatter opt-out

If a source document carries either of these in its frontmatter,
`identify_extractable_atoms` returns an empty list and no notes are
written:

```yaml
---
title: Customer-confidential debrief
cross_repo: false           # explicit opt-out
---
```

```yaml
---
title: One-time hotfix log
disposition: none           # equivalent spelling
---
```

## Threshold tuning

`CROSS_REPO_THRESHOLD = 6`, `LOCAL_THRESHOLD = 3`, `MIN_CONTENT_LENGTH
= 500`. Override at runtime by monkey-patching from your own bootstrap
module — they are intentionally module-level and free to mutate.

```python
import sillok.yeonryun.disposition as yd
yd.CROSS_REPO_THRESHOLD = 8        # stricter promotion
yd.MIN_CONTENT_LENGTH = 1000
```

## Bilingual signals

Reusability patterns ship bilingual (English + Korean) by default. To
add domain-specific signals, append to `REUSABLE_PATTERNS` in your
bootstrap before scoring:

```python
import sillok.yeonryun.disposition as yd
yd.REUSABLE_PATTERNS.append(
    (r"(?:RFP|RFI|proposal|제안서)", "template", 3),
)
```

## See also

- [Recipe — Search a vault with `bongsu`](search-vault-with-bongsu.md)
- Module reference: `sillok.yeonryun.disposition`
- Karpathy LLM Wiki — Sillok's `yeonryun` is the *Lint / Auto-grow*
  half of the pattern (deciding what graduates from raw → wiki).
