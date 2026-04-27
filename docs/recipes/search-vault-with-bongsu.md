# Recipe — Search a vault with `bongsu`

> Build a queryable index of a markdown vault in seconds, then filter
> notes by frontmatter (scope · type · retrieval tier) or full-text
> body match.

## When to use

- You have a folder of `.md` notes (Obsidian vault, docs site, personal
  wiki) and want a quick programmatic search.
- You want to drive routing or curation downstream — the result is a
  plain `list[dict]`.
- You don't want to set up Elasticsearch / Meilisearch / Typesense.

## CLI

```bash
# Stats for a vault (no query)
python -m sillok.bongsu.search --vault ~/Documents/my-vault --stats

# Frontmatter-only filter
python -m sillok.bongsu.search --vault ~/Documents/my-vault \
    --scope acme --type pattern --tier A --limit 10

# Frontmatter + body full-text (uses ripgrep when available, grep otherwise)
python -m sillok.bongsu.search --vault ~/Documents/my-vault \
    --scope acme --query "pricing" --format full

# JSON for piping into other tools
python -m sillok.bongsu.search --vault ~/Documents/my-vault \
    --type decision --format json | jq '.[] | .title'
```

## Python API

```python
from pathlib import Path
from sillok.bongsu import build_index, filter_notes, fulltext_search

vault = Path("~/Documents/my-vault").expanduser()

notes = build_index(vault)
acme_patterns = filter_notes(notes, scope="acme", note_type="pattern", tier="A")

# Body match across the whole vault, then intersect with the filter.
hits = fulltext_search(vault, ("."), query="pricing")
matched = [n for n in acme_patterns if n["_path"] in hits]

for n in matched[:5]:
    print(f"{n['_path']:40s}  {n.get('title', '?')}")
```

## Scope aliases

If your vault has historical aliases (e.g. `acme-corp`, `acme-inc` are
both the same client today), drop a `.sillok/scope-aliases.yaml` at the
vault root:

```yaml
acme-corp: acme
acme-inc: acme
acme-international: acme
```

`build_index` + `filter_notes` honor it automatically — `--scope acme`
will return notes whose frontmatter still says `acme-corp`.

## Excludes

`.git`, `.obsidian`, `.sillok`, `.sillok-janggyeong`, `node_modules`,
`__pycache__`, `.venv` are skipped by default. Pass an explicit
`excludes=` tuple to `build_index` to override.

## See also

- [Recipe — Decide what's reusable with `yeonryun`](decide-reusability-with-yeonryun.md)
- Module reference: `sillok.bongsu.search`
- Karpathy LLM Wiki — Sillok's `bongsu` is the *Query* half of the pattern.
