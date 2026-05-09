# Sillok MCP — 5-Minute Quickstart

> **Status**: shipped in v0.2.0a1 · Issue [#4](https://github.com/sillok-os/sillok/issues/4)
> **Module**: `sillok.tongsa`
> **Three tools**: `sillok.list_packs` · `sillok.route` · `sillok.search`

## Install

```bash
pip install 'sillok[mcp]'
```

This pulls the optional `mcp>=0.1.0` package on top of the core install.

## Verify (no server start required)

```bash
# What tools will the server register?
python -m sillok.tongsa tools

# What do the routing reason codes mean?
python -m sillok.tongsa describe

# Exercise all three tools in-process (CI-friendly smoke)
python -m sillok.tongsa smoke --message "[pm] kickoff a new feature"
```

Expected smoke output:

```
─── sillok.list_packs ───
10 packs registered
  e.g. pm-enhanced               PM Lifecycle Pack — Plan / Doing / Done / Release / Audit
─── sillok.route ───
  pm-enhanced               score=209.5 codes=['R1', 'R3', 'R4']
  reason codes (overall): ['R1', 'R3', 'R4']
─── sillok.search ───
  packs/methodology/pm-enhanced.md
```

## Wire into Cursor

Place `examples/cursor-mcp-config.json` content under your global `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "sillok": {
      "command": "python",
      "args": ["-m", "sillok.tongsa", "serve", "--transport", "stdio"],
      "env": { "PYTHONUNBUFFERED": "1" }
    }
  }
}
```

Restart Cursor. From a chat:

> "List my Sillok packs."

Cursor will route to `sillok.list_packs`. The first invocation may take ~1 second while the registry parses.

## Wire into Claude Code

```bash
claude mcp add sillok python -m sillok.tongsa serve --transport stdio
```

Or place `examples/claude-code-mcp-config.json` in your project's `.claude/mcp.json`.

## Reason codes (R1-R7)

Every `sillok.route` response includes `reason_codes` for audit-ability:

| Code | Meaning |
|:-:|---|
| **R1** | explicit-trigger match (e.g., `[pm]` → pm-enhanced) — highest weight |
| **R2** | keyword-contains match (e.g., "risk register" → risk-uncertainty) |
| **R3** | precedence tie-break (10% weight) |
| **R4** | discovery_tier full elevation (precedence ≥ 90) |
| **R5** | discovery_tier full elevation (last_used_12d ≥ 5) |
| **R6** | top-K cutoff — candidate truncated below cut-line |
| **R7** | empty-candidate fallback — no triggers matched any pack |

Run `python -m sillok.tongsa describe` to print the same table from the live install.

## What ships in v0.2.0a1

- ✅ stdio transport (works with Cursor, Claude Code, Continue, Codex CLI)
- ✅ SSE transport (HTTP-style clients) via `--transport sse`
- ✅ Localhost-only enforcement (no auth → no remote binds)
- ✅ Three tools wrapping the live registry + router + vault search
- ✅ Reason codes R1-R7 emitted on every routing decision

## What does not ship in v0.2.0a1

- ❌ Authentication / token-based access — defer to v0.3.0
- ❌ Multi-tenant scoping (`beopjeon`) — defer to 1.0.0 GA
- ❌ Plugin tool discovery (`dure`) — separate issue
- ❌ Streaming responses — initial: blocking only

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `ImportError: sillok.tongsa.server requires 'mcp'` | Optional dep not installed | `pip install 'sillok[mcp]'` |
| `ERROR: host 0.0.0.0 is not localhost` | Tried to bind non-localhost without auth | Use `--host 127.0.0.1` (default). Auth lands in v0.3.0. |
| Cursor doesn't see the tool | MCP config typo | Run `python -m sillok.tongsa tools` to confirm install, then restart Cursor. |

## Logs

The server logs each routing decision with its reason codes to stderr (so MCP-stdio doesn't conflict with the JSON-RPC stdout channel). Pipe stderr to your IDE log of choice.
