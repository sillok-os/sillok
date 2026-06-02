# SPDX-License-Identifier: Apache-2.0
"""sillok.cli — the unified ``sillok`` command.

A thin dispatcher over the per-module CLIs that already ship. Subcommands are
imported lazily and tolerantly: a module whose optional dependency is missing
(e.g. ``tongsa`` needing an MCP runtime) degrades to a clear error for that one
subcommand instead of breaking the whole ``sillok`` command.

    sillok --version
    sillok route "Draft a Q3 strategy for Acme"
    sillok eval run
    sillok sangso list-proposals
"""

from __future__ import annotations

import importlib

import click

from sillok import __version__

# subcommand name -> module exposing a ``cli`` click group
_LAZY_SUBCOMMANDS: dict[str, str] = {
    "eval": "sillok.eval.__main__",
    "sangso": "sillok.sangso.__main__",
    "schemas": "sillok.schemas.__main__",
    "tongsa": "sillok.tongsa.__main__",
}


class _LazyGroup(click.Group):
    """A click group that imports its module subcommands on demand."""

    def list_commands(self, ctx: click.Context) -> list[str]:
        return sorted({*_LAZY_SUBCOMMANDS, *super().list_commands(ctx)})

    def get_command(self, ctx: click.Context, cmd_name: str) -> click.Command | None:
        local = super().get_command(ctx, cmd_name)
        if local is not None:
            return local
        target = _LAZY_SUBCOMMANDS.get(cmd_name)
        if target is None:
            return None
        try:
            module = importlib.import_module(target)
            group = module.cli
        except Exception as exc:  # missing optional dep — fail only this subcommand
            message = str(exc)

            @click.command(
                name=cmd_name,
                help=f"(unavailable — {message})",
                context_settings={"ignore_unknown_options": True},
            )
            @click.argument("args", nargs=-1, type=click.UNPROCESSED)
            def _unavailable(args: tuple[str, ...]) -> None:
                raise click.ClickException(f"`sillok {cmd_name}` is unavailable: {message}")

            return _unavailable
        if isinstance(group, click.Command):
            return group
        return None


@click.group(cls=_LazyGroup)
@click.version_option(version=__version__, prog_name="sillok")
def main() -> None:
    """Sillok — an auditable LLM Wiki control plane.

    Run a subcommand below, or use the per-module form
    ``python -m sillok.<module>`` for anything not yet surfaced here.
    """


@main.command()
@click.argument("message")
@click.option("--top-k", default=5, show_default=True, help="number of candidate packs")
def route(message: str, top_k: int) -> None:
    """Route MESSAGE to candidate packs (Tier 1 keyword match)."""
    from sillok.naru import router_2tier

    raise SystemExit(router_2tier.main(["--message", message, "--top-k", str(top_k)]))


if __name__ == "__main__":
    main()
