# mcp_server

Sillok's Model Context Protocol bridge ships **in-tree** as
`sillok.tongsa`, behind the optional `mcp` extra:

```bash
pip install --pre 'sillok[mcp]'
python -m sillok.tongsa serve --transport stdio
```

There is no separate `sillok-tongsa` or `sillok-mcp` distribution on
PyPI — earlier drafts of these docs named packages that were never
published. This directory is reserved for a future standalone split
in **Phase 1 (PR-D — MCP first-class)**.

Until then, MCP integration is documented in:
- Public README §IDE / AI client integration (7-client matrix)
- `integrations/claude-code/README.md`
