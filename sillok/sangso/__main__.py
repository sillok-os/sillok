"""sillok.sangso.__main__ — CLI for proposal-only 4-gate governance.

Sub-commands::

    python -m sillok.sangso propose <pack_id> --diff <file.md>
    python -m sillok.sangso list [--all]
    python -m sillok.sangso show <proposal_id>
    python -m sillok.sangso accept <proposal_id>

The ``accept`` sub-command requires **interactive** y/N confirmation. There
is no ``--force`` flag and no API endpoint for auto-merge. This is the
hard guard against prompt drift.
"""
from __future__ import annotations

import sys
from pathlib import Path

import click

from sillok.naru.router_2tier import load_registry
from sillok.sangso.gates import gate_approval_artifact, run_all_gates
from sillok.sangso.proposal import Proposal


def _repo_root() -> Path:
    """Heuristic repo root: cwd or the parent of packs/registry.yaml."""
    cwd = Path.cwd()
    if (cwd / "packs" / "registry.yaml").exists():
        return cwd
    for parent in cwd.parents:
        if (parent / "packs" / "registry.yaml").exists():
            return parent
    return cwd


def _proposals_dir(repo_root: Path) -> Path:
    return repo_root / "proposals"


@click.group()
def cli() -> None:
    """Sillok proposal-only governance — `sangso`."""


@cli.command("propose")
@click.argument("pack_id")
@click.option(
    "--diff",
    "diff_path",
    required=True,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Path to the proposed pack body (.md file).",
)
def propose(pack_id: str, diff_path: Path) -> None:
    """Run gates 1-4 against a proposed pack body and emit a proposal artifact."""
    repo_root = _repo_root()
    packs = load_registry(repo_root / "packs" / "registry.yaml")
    matching = next((p for p in packs if p.get("id") == pack_id), None)
    if matching is None:
        click.echo(f"ERROR: pack {pack_id!r} not found in registry", err=True)
        sys.exit(2)

    current_path = repo_root / matching["path"]
    if not current_path.exists():
        click.echo(f"ERROR: pack body not found at {current_path}", err=True)
        sys.exit(2)

    current_text = current_path.read_text(encoding="utf-8")
    proposed_text = diff_path.read_text(encoding="utf-8")

    gates = run_all_gates(pack_id, current_text, proposed_text, repo_root)
    approval, artifact_path = gate_approval_artifact(
        pack_id=pack_id,
        diff_source=diff_path,
        gates=gates,
        proposals_dir=_proposals_dir(repo_root),
    )
    gates.append(approval)

    click.echo(f"Pack: {pack_id}")
    click.echo(f"Diff source: {diff_path}")
    click.echo("─" * 60)
    for g in gates:
        mark = "OK  " if g.passed else "FAIL"
        click.echo(f"[{mark}] {g.gate:<14} {g.summary}")
    click.echo("─" * 60)
    click.echo(f"Artifact: {artifact_path}")

    if not all(g.passed for g in gates):
        click.echo("\nNote: one or more gates failed. Review the artifact before accept.", err=True)
        sys.exit(1)


@cli.command("list")
def list_proposals() -> None:
    """List proposals under ``proposals/``."""
    root = _proposals_dir(_repo_root())
    if not root.exists():
        click.echo("(no proposals directory yet)")
        return
    found = sorted(root.glob("*.md"))
    if not found:
        click.echo("(no proposals)")
        return
    for path in found:
        try:
            summary = Proposal.load(path)
        except Exception as exc:  # noqa: BLE001
            click.echo(f"  ! unparseable: {path.name} — {exc}", err=True)
            continue
        mark = "✓" if summary.upstream_passed else "✗"
        click.echo(f"  {mark} {summary.id}  pack={summary.pack_id}")


@cli.command("show")
@click.argument("proposal_id")
def show(proposal_id: str) -> None:
    """Render a proposal artifact to stdout."""
    path = _proposals_dir(_repo_root()) / f"{proposal_id}.md"
    if not path.exists():
        click.echo(f"ERROR: proposal not found: {path}", err=True)
        sys.exit(2)
    click.echo(path.read_text(encoding="utf-8"))


@cli.command("accept")
@click.argument("proposal_id")
def accept(proposal_id: str) -> None:
    """Apply a proposal — *requires interactive confirmation*."""
    repo_root = _repo_root()
    proposals_dir = _proposals_dir(repo_root)
    path = proposals_dir / f"{proposal_id}.md"
    if not path.exists():
        click.echo(f"ERROR: proposal not found: {path}", err=True)
        sys.exit(2)

    summary = Proposal.load(path)
    if not summary.upstream_passed:
        click.echo(
            "ERROR: upstream gates did not pass — accept refused.\n"
            "       Resolve gate failures and re-propose, or accept manually outside the harness.",
            err=True,
        )
        sys.exit(1)

    if summary.diff_source is None or not Path(summary.diff_source).exists():
        click.echo(
            f"ERROR: diff source no longer exists at {summary.diff_source}", err=True
        )
        sys.exit(2)

    packs = load_registry(repo_root / "packs" / "registry.yaml")
    matching = next((p for p in packs if p.get("id") == summary.pack_id), None)
    if matching is None:
        click.echo(f"ERROR: pack {summary.pack_id!r} no longer in registry", err=True)
        sys.exit(2)
    target = repo_root / matching["path"]

    click.echo(f"About to overwrite:  {target}")
    click.echo(f"With contents from:  {summary.diff_source}")
    if not sys.stdin.isatty():
        click.echo(
            "\nERROR: accept requires an interactive TTY. There is no --force flag.",
            err=True,
        )
        sys.exit(1)
    confirmation = click.prompt(
        "\nType 'apply' (lowercase, no quotes) to proceed",
        default="",
        show_default=False,
    )
    if confirmation.strip() != "apply":
        click.echo("Aborted (no changes made).")
        sys.exit(0)

    proposed_text = Path(summary.diff_source).read_text(encoding="utf-8")
    target.write_text(proposed_text, encoding="utf-8")
    click.echo(f"Applied. Updated {target}.")


if __name__ == "__main__":
    cli()
