# Kernel example (experimental · 0.4.0)

Synthetic configuration for `python -m sillok.kernel.hook`. Nothing here is
real user data — replace the work types, playbook items and paths with your own.

| File | What it configures |
|---|---|
| `kernel.json` | where state lives, which files to load, playbook mode, recall paths |
| `work-types.json` | work-type profiles for **sacho** (work context): `triggers` that name the work explicitly, path prefixes that count as action evidence, guide documents |
| `playbook-items.json` | lessons for **gyeongyeon** (playbook), keyed by work type |

Memory notes for **chunchugwan** (recall) are Markdown files with front matter
(`name`, `description`, optional `status: superseded`) in `recall.memory_dir`.

## Claude Code wiring

`.claude/settings.json`:

```json
{
  "hooks": {
    "UserPromptSubmit": [{"hooks": [{"type": "command",
      "command": "python -m sillok.kernel.hook --config ~/.sillok/kernel.json"}]}],
    "SessionStart": [{"matcher": "compact", "hooks": [{"type": "command",
      "command": "python -m sillok.kernel.hook --config ~/.sillok/kernel.json"}]}],
    "Stop": [{"hooks": [{"type": "command",
      "command": "python -m sillok.eval.request_coverage"}]}]
  }
}
```

## Rolling it out

1. Start with the playbook in `shadow` mode: nothing is shown, control
   counters (`sh`/`sx`) accumulate.
2. Switch to `auto` (`SILLOK_PLAYBOOK_MODE=auto`) and compare treatment
   counters (`h`/`x`) against the shadow period before keeping it on.
3. `Playbook.promote_candidates()` lists lessons helpful in ≥ 3 sessions with
   no harm — turning one into a rule or test is your decision.

Off switches: `SILLOK_WORK_CONTEXT=off`, `SILLOK_PLAYBOOK_MODE=off`,
`SILLOK_MEMORY_RECALL=off`, `SILLOK_CONTEXT_BUDGET=off`, `SILLOK_REQUEST_COVERAGE=off`.
