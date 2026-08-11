# Sillok MCP — 5-Minute Quickstart

> **Status**: shipped in v0.2.0a1 · Issue [#4](https://github.com/sillok-os/sillok/issues/4)
> **Module**: `sillok.tongsa`
> **Three tools**: `sillok.list_packs` · `sillok.route` · `sillok.search`

## Install

```bash
pip install --pre 'sillok[mcp]'
```

This pulls the optional `mcp>=1.2,<2` package on top of the core install.

Two things that bite without `--pre` and without the pin:

- **`--pre` is required.** The non-prerelease `sillok` on PyPI is the `0.0.1`
  name-reservation placeholder — it installs an empty package with no
  submodules, so `python -m sillok.tongsa` fails with `No module named`.
- **MCP SDK 2.0 is incompatible.** It removed `mcp.server.fastmcp`, which
  the bridge imports. Installs from before this pin landed may hold
  `mcp==2.x`; fix with `pip install 'mcp>=1.2,<2'`.

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
      "env": { "PYTHONUNBUFFERED": "1", "PYTHONIOENCODING": "utf-8" }
    }
  }
}
```

Restart Cursor. From a chat:

> "List my Sillok packs."

Cursor will route to `sillok.list_packs`. The first invocation may take ~1 second while the registry parses.

## Wire into Claude Code

```bash
claude mcp add sillok -- python -m sillok.tongsa serve --transport stdio
```

Or copy `examples/claude-code-mcp-config.json` to **`.mcp.json` in your project root**
(not `.claude/mcp.json`, and not `settings.json`), then **restart Claude Code**.
MCP servers connect at startup, so a config written mid-session stays invisible
until the next launch.

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
| `ModuleNotFoundError: No module named 'mcp.server.fastmcp'` | MCP SDK 2.0 installed | `pip install 'mcp>=1.2,<2'` — 2.0 removed that module. |
| Claude Code / Cursor still shows no tools after config | Host connects MCP servers at startup | Restart the host. A `.mcp.json` written mid-session is not loaded. |
| `No Sillok pack registry found` | cwd is not a checkout and the install predates bundled packs | `pip install --pre --force-reinstall 'sillok[mcp]'`, or set `SILLOK_REGISTRY=/path/to/packs/registry.yaml`. |
| `UnicodeEncodeError: 'cp949' codec can't encode character '\u2014'` | Windows console code page | Fixed in-process; on older installs set `PYTHONIOENCODING=utf-8` (also in the MCP `env` block). |

## Logs

The server logs each routing decision with its reason codes to stderr (so MCP-stdio doesn't conflict with the JSON-RPC stdout channel). Pipe stderr to your IDE log of choice.
