# mcp_server

Sillok's Model Context Protocol bridge ships as a separate package
(`pip install sillok-tongsa`) so MCP-only consumers do not pull in the
core. This directory is reserved for the in-tree development copy
that lands in **Phase 1 (PR-D — MCP first-class)**.

Until then, MCP integration is documented in:
- Public README §IDE / AI client integration (7-client matrix)
- `integrations/claude-code/README.md`
