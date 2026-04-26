# integrations/claude-code

Bridge between Sillok and Claude Code (Anthropic's CLI / IDE harness).

## Status

| | |
|---|---|
| Schedule | Phase 1 (PR-D — MCP first-class) |
| Current | 🟡 placeholder — generic MCP path already documented in `04-prototypes/sillok-public-README.md` §IDE / AI client integration |
| Activation | when `sillok-tongsa` is published as a separate PyPI package |

## What this integration adds (target experience)

Sillok speaks Model Context Protocol (MCP), so any MCP-aware host
(Claude Code, Codex CLI, Gemini CLI, Cursor, Continue, Claude Desktop,
Codex Desktop) sees the same packs and corpus. This directory will hold
**Claude Code-specific niceties** on top of generic MCP:

1. **Slash-command bindings** — `/sillok-route`, `/sillok-ingest`, etc.
   wired into Claude Code's command palette.
2. **Skill manifest** — Sillok packs surfaced as Claude Code Skills so
   the model can discover them via the standard skill-discovery flow.
3. **Sub-agent presets** — `naru-router`, `bongsu-retriever`,
   `sangso-reviewer` as named sub-agents for `Task()` invocations.
4. **Log streaming** — Sillok telemetry rows mirrored into the Claude
   Code session log for unified replay.

## Generic MCP setup (works today)

Add to `~/.claude/settings.json` or a project-local `.mcp.json`:

```json
{
  "mcpServers": {
    "sillok": {
      "command": "sillok-tongsa",
      "args": ["serve", "--stdio"]
    }
  }
}
```

This works for **all** seven supported AI clients with the appropriate
file location. See the public README's matrix for client-by-client
JSON snippets.

## Non-goals

- Distributing the Sillok PyPI package via the Claude Code plugin
  catalog — that is a host concern.
- Writing back to your Claude Code workspace — the bridge is
  read-mostly (it writes only its own telemetry rows).
