"""sillok.tongsa.server — FastMCP server binding.

Wraps :mod:`sillok.tongsa.tools` as MCP tools using the official
``mcp.server.fastmcp.FastMCP`` adapter from the Python MCP SDK.

The ``mcp`` package is an *optional* dependency (``pip install sillok[mcp]``).
``import sillok.tongsa.server`` will fail without it; ``sillok.tongsa.tools``
remains importable in any environment.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from sillok.tongsa.tools import (
    sillok_list_packs,
    sillok_route,
    sillok_search,
)


def build_server(name: str = "sillok"):
    """Construct an MCP server with the three Sillok tools registered.

    Returns:
        ``mcp.server.fastmcp.FastMCP`` instance.

    Raises:
        ImportError: if the optional ``mcp`` package is not installed.
            Run ``pip install sillok[mcp]`` to fix.
    """
    try:
        from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]
    except ImportError as exc:  # pragma: no cover — exercised at runtime only
        raise ImportError(
            "sillok.tongsa.server requires the optional 'mcp' package. "
            "Install with: pip install sillok[mcp]"
        ) from exc

    server = FastMCP(name)

    @server.tool(
        name="sillok.list_packs",
        description="List every registered Sillok pack with title, category, "
        "precedence, and intent tags.",
    )
    def list_packs() -> list[dict[str, Any]]:
        return sillok_list_packs()

    @server.tool(
        name="sillok.route",
        description="Route a natural-language message to top-K matching "
        "Sillok packs. Returns candidate packs with reason codes R1-R7.",
    )
    def route(message: str, top_k: int = 3) -> dict[str, Any]:
        return sillok_route(message, top_k=top_k)

    @server.tool(
        name="sillok.search",
        description="Full-text search across a vault directory. Defaults "
        "to packs/ so it works in-repo without setup.",
    )
    def search(query: str, vault_path: str | None = None, pack: str | None = None, k: int = 5) -> list[dict[str, Any]]:
        return sillok_search(
            query=query,
            vault_path=Path(vault_path) if vault_path else None,
            pack=pack,
            k=k,
        )

    return server
