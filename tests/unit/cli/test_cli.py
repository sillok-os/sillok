"""Unit tests for the unified sillok CLI dispatcher."""

from __future__ import annotations

from click.testing import CliRunner

from sillok.cli import main


def test_version_runs() -> None:
    result = CliRunner().invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "sillok" in result.output


def test_help_lists_module_subcommands() -> None:
    result = CliRunner().invoke(main, ["--help"])
    assert result.exit_code == 0
    for sub in ("eval", "sangso", "schemas", "tongsa", "route"):
        assert sub in result.output


def test_lazy_subcommand_mounts() -> None:
    # eval is a real click group; its --help must resolve via lazy import.
    result = CliRunner().invoke(main, ["eval", "--help"])
    assert result.exit_code == 0


def test_unknown_subcommand_errors_cleanly() -> None:
    result = CliRunner().invoke(main, ["does-not-exist"])
    assert result.exit_code != 0
