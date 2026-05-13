"""sillok.schemas.__main__ — schema validators CLI.

Sub-commands::

    python -m sillok.schemas validate-skills [--packs-dir DIR] [--strict]

``validate-skills`` enforces the agentskills.io v0.9 frontmatter contract
across pack body files (see ``skills_v09.py``).
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import click


@click.group()
def cli() -> None:
    """Sillok schema validators."""


@cli.command("validate-skills")
@click.option(
    "--packs-dir",
    default="packs",
    show_default=True,
    help="Root directory containing pack body files.",
)
@click.option(
    "--strict/--no-strict",
    default=True,
    show_default=True,
    help="Fail on missing v0.9 frontmatter (strict) or skip silently (--no-strict).",
)
def validate_skills(packs_dir: str, strict: bool) -> None:
    """Validate agentskills.io v0.9 frontmatter across pack body files."""
    from sillok.schemas.skills_v09 import SkillsV09Frontmatter

    failures: list[tuple[Path, str]] = []
    checked = 0
    skipped = 0

    for path in sorted(Path(packs_dir).rglob("*.md")):
        if path.name == "README.md":
            continue
        text = path.read_text(encoding="utf-8")
        frontmatter = _extract_frontmatter(text)
        if frontmatter is None:
            failures.append((path, "no frontmatter block"))
            continue

        v09 = {
            key: frontmatter[key]
            for key in ("name", "description", "capabilities", "triggers")
            if key in frontmatter
        }
        if not v09:
            if strict:
                failures.append(
                    (path, "missing v0.9 fields (name/description/capabilities/triggers)")
                )
            else:
                skipped += 1
            continue

        try:
            SkillsV09Frontmatter.model_validate(v09)
            checked += 1
        except Exception as exc:  # noqa: BLE001 — surface any validation error
            failures.append((path, str(exc)))

    if failures:
        for path, reason in failures:
            click.echo(f"FAIL  {path}: {reason}", err=True)
        click.echo(
            f"\n{len(failures)} pack(s) failed v0.9 validation; "
            f"{checked} passed; {skipped} skipped",
            err=True,
        )
        sys.exit(1)
    click.echo(
        f"OK: {checked} pack(s) validate against agentskills.io v0.9 frontmatter "
        f"({skipped} skipped)"
    )


def _extract_frontmatter(text: str) -> dict[str, Any] | None:
    """Extract YAML frontmatter from a markdown body. Returns ``None`` on miss."""
    import yaml

    if not text.startswith("---\n"):
        return None
    rest = text[4:]
    end = rest.find("\n---\n")
    if end < 0:
        return None
    block = rest[:end]
    try:
        loaded = yaml.safe_load(block)
    except yaml.YAMLError:
        return None
    return loaded or {}


if __name__ == "__main__":
    cli()
