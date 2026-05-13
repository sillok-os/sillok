"""sillok.tongsa — MCP (Model Context Protocol) bridge.

Top 10 Feature #6: expose Sillok over MCP so Cursor / Continue / Codex CLI
/ Claude Code / ChatGPT Desktop can use the router and corpus without
forking off Sillok's native registry.

Three tools are exposed (kept deliberately small in v0.2.0a1):

- ``sillok.search``     — wraps ``bongsu.fulltext_search`` over a vault dir
- ``sillok.route``      — wraps ``naru.router_2tier.tier1_match``
- ``sillok.list_packs`` — wraps ``packs/registry.yaml``

Every routing decision is tagged with a reason code R1-R7 (see
``tools.classify_reason_codes``) so tool-side audit logs stay structured.

CLI::

    python -m sillok.tongsa serve --port 7301

Server install: ``pip install sillok[mcp]``.
"""
from __future__ import annotations

from .tools import (
    REASON_CODES,
    classify_reason_codes,
    sillok_list_packs,
    sillok_route,
    sillok_search,
)

__all__ = [
    "REASON_CODES",
    "classify_reason_codes",
    "sillok_list_packs",
    "sillok_route",
    "sillok_search",
]
