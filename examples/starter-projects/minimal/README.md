# minimal — 60-second starter

The smallest possible Sillok setup. Single user, single vault, no IDE
integration, no overlays. If `pip install sillok` works for you, this
example should run end-to-end.

> **Status (2026-04-26)**: this directory currently documents the
> **target** experience for `0.1.0a1+`. The current PyPI release `0.0.1`
> is a placeholder; install will not actually wire the CLI.

## What you will produce

A vault directory at `~/Documents/my-vault` with:

- 2 markdown notes (you can replace these with your own)
- a Sillok corpus index at `.sillok-janggyeong/index.jsonl`
- a successful `sillok route "..."` invocation that picks at least 1 starter pack

## Steps

```bash
# 1. install
pip install sillok                   # 0.1.0a1+ for real functionality
sillok --version

# 2. create a vault and seed it
mkdir -p ~/Documents/my-vault
cat > ~/Documents/my-vault/note-1.md <<EOF
---
title: Q3 platform plan
tags: [pm, planning]
---
We need to scope the Q3 platform release across 4 squads.
EOF

cat > ~/Documents/my-vault/note-2.md <<EOF
---
title: Risk register seed
tags: [risk]
---
Initial risks for the Q3 release: capacity, scope creep, dep on the data team.
EOF

# 3. ingest (md only at this Phase 0; multi-format in PR-K)
python -m sillok.pyeonchan.ingest_md ~/Documents/my-vault
# → indexed 2 markdown file(s) under ~/Documents/my-vault

# 4. route a query
sillok route "[pm] start a Q3 platform milestone"
# Expected:
#   applied prompt packs: pm-enhanced
#   tier1 candidates (1):
#     [   full] pm-enhanced  score=  ...

# 5. (optional) keep the index fresh while you work
python -m sillok.pyeonchan.watcher ~/Documents/my-vault --interval 5 &
```

## What is happening

| Step | Top 10 Feature | Module |
|---|---|---|
| 3. ingest | #1 Multi-format Auto-Ingest | `sillok.pyeonchan` |
| 4. route | #2 Two-Stage Routing + #3 Typed Pack Registry | `sillok.naru` + `sillok.jikji` |
| 5. watch | #1 (continuous) | `sillok.pyeonchan.watcher` |

Top 10 Features #4–#10 (governance, multi-tenant, MCP, plugins, eval,
cross-tool plan, failure taxonomy) are **not** exercised by this minimal
example — they are covered in `examples/multi-pack/` and
`examples/multi-tenant/`.

## Common pitfalls

| Symptom | Cause | Fix |
|---|---|---|
| `sillok: command not found` | PATH issue after `pip install --user` | add `~/.local/bin` to PATH |
| `0 markdown files indexed` | empty vault or all in excluded dirs | check `--exclude` flags; default skips `.git`, `.obsidian`, `.sillok`, `node_modules`, `__pycache__`, `.venv` |
| `tier1 returned 0 candidates` | message has no trigger keyword for any pack | try with explicit trigger: `[pm]`, `[risk]`, `[itil]`, etc. |

## Next steps

- `examples/starter-projects/multi-pack/` — chain a domain pack + a quality-guard
- `examples/starter-projects/multi-tenant/` — per-client overlays
- `docs/tutorials/` — longer guides as they land

## Cleanup

```bash
rm -rf ~/Documents/my-vault
pip uninstall sillok
```
