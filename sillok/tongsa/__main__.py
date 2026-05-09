"""sillok.tongsa.__main__ — MCP server CLI.

Sub-commands::

    python -m sillok.tongsa serve [--port 7301] [--host 127.0.0.1]
    python -m sillok.tongsa tools          # list registered tools (no server)
    python -m sillok.tongsa describe       # human description of each tool

Localhost-only in v0.2.0a1 — auth lands in v0.3.0.
"""
from __future__ import annotations

import sys

import click

from sillok.tongsa.tools import (
    REASON_CODES,
    sillok_list_packs,
    sillok_route,
    sillok_search,
)


@click.group()
def cli() -> None:
    """Sillok MCP bridge — `tongsa`."""


@cli.command("serve")
@click.option(
    "--port",
    default=7301,
    show_default=True,
    type=int,
    help="Port to bind. Localhost-only in v0.2.0a1.",
)
@click.option(
    "--host",
    default="127.0.0.1",
    show_default=True,
    help="Host to bind. Localhost-only in v0.2.0a1 — do not change without auth.",
)
@click.option(
    "--transport",
    default="stdio",
    show_default=True,
    type=click.Choice(["stdio", "sse"]),
    help="MCP transport. stdio for IDE plugins; sse for HTTP-style clients.",
)
def serve(port: int, host: str, transport: str) -> None:
    """Start the MCP server."""
    if host not in {"127.0.0.1", "localhost", "::1"}:
        click.echo(
            f"ERROR: host {host!r} is not localhost. v0.2.0a1 has no auth — "
            "non-localhost binds are refused. Auth lands in v0.3.0.",
            err=True,
        )
        sys.exit(1)
    try:
        from sillok.tongsa.server import build_server
    except ImportError as exc:
        click.echo(f"ERROR: {exc}", err=True)
        sys.exit(2)

    server = build_server()
    if transport == "stdio":
        click.echo(f"sillok MCP server (stdio) — 3 tools registered", err=True)
        server.run()
    else:  # sse
        click.echo(f"sillok MCP server (sse) on {host}:{port} — 3 tools registered", err=True)
        server.run(transport="sse", host=host, port=port)


@cli.command("tools")
def list_tools() -> None:
    """List the 3 tools the server registers (no server start required)."""
    tools = [
        ("sillok.list_packs", "List registered packs (id, title, category, precedence)"),
        ("sillok.route", "Route NL message → top-K packs + reason codes R1-R7"),
        ("sillok.search", "Full-text search a vault directory (defaults to packs/)"),
    ]
    for name, desc in tools:
        click.echo(f"{name:<22} {desc}")


@cli.command("describe")
def describe() -> None:
    """Describe the reason codes (R1-R7) attached to routing decisions."""
    click.echo("Reason codes (every routing decision is tagged):")
    for code, meaning in REASON_CODES.items():
        click.echo(f"  {code}  {meaning}")


@cli.command("smoke")
@click.option("--message", default="[pm] kickoff a new feature", show_default=True)
def smoke(message: str) -> None:
    """One-shot tool exercise (no MCP server) — useful for CI smoke."""
    click.echo("─── sillok.list_packs ───")
    packs = sillok_list_packs()
    click.echo(f"{len(packs)} packs registered")
    if packs:
        click.echo(f"  e.g. {packs[0]['id']:<25} {packs[0]['title']}")

    click.echo("─── sillok.route ───")
    routed = sillok_route(message, top_k=3)
    for cand in routed["packs"]:
        click.echo(
            f"  {cand['pack_id']:<25} score={cand['score']} codes={cand['reason_codes']}"
        )
    click.echo(f"  reason codes (overall): {routed['reason_codes']}")

    click.echo("─── sillok.search ───")
    hits = sillok_search(query="risk", k=3)
    for hit in hits:
        click.echo(f"  {hit['path']}")


if __name__ == "__main__":
    cli()
