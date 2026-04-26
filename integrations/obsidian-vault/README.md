# integrations/obsidian-vault

Bridge between Sillok's vault-resident corpus (Janggyeong) and an
existing Obsidian vault.

## Status

| | |
|---|---|
| Schedule | Phase 2 (PR-F — Knowledge loop callback / `bongsu.post_update` auto hook) |
| Current | 🟡 placeholder — Sillok already reads md + frontmatter from any directory; this integration adds Obsidian-specific niceties on top |
| Activation | when `sillok.bongsu.post_update` lands its `--auto-knowledge-loop` flag |

## What this integration adds (target experience)

If your vault is already an Obsidian vault, the bridge handles three
Obsidian-specific concerns that the generic `sillok.pyeonchan` ingest
does not:

1. **Backlink graph awareness** — wiki-links (`[[note]]`) become atom
   `related_atoms` references.
2. **Aliases and tags** — Obsidian frontmatter `aliases:` and `tags:`
   are surfaced into the index for retrieval.
3. **Daily notes / templates** — configured Obsidian folders
   (`Daily/`, `Templates/`) are skipped or specially indexed per
   user preference.

## Today (without the bridge)

You can already use Sillok against an Obsidian vault — just point
ingest at the vault root:

```bash
python -m sillok.pyeonchan.ingest_md ~/Documents/MyObsidianVault
```

The default `excludes` list (`.obsidian`) already handles the metadata
folder. You will simply not get backlink-graph features yet.

## Configuration knobs (planned)

```toml
# .sillok/config.toml (when bridge ships)
[integrations.obsidian]
enabled = true
backlink_index = true
respect_excluded_folders = true   # honor Obsidian's own .excludeFolders
template_folders = ["Templates"]
daily_notes_folder = "Daily"
```

## Non-goals

- Replacing Obsidian as an editor — Sillok does not open `.md` files
  in any UI.
- Handling Obsidian Sync conflicts — those are a Sync product concern.
- Indexing Obsidian Canvas (`.canvas`) — only `.md` is in scope.
