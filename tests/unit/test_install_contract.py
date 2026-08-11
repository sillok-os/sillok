"""Regression guards for the fresh-install path.

Every assertion here maps to a defect that made `pip install` + MCP setup
fail end-to-end for new users:

- the wheel shipped code but no packs, and the registry was looked up at a
  cwd-relative path, so any host that launches Sillok from its *own*
  project directory (every IDE MCP server) got ``FileNotFoundError``;
- the ``mcp`` extra had no upper bound, so fresh installs resolved to MCP
  SDK 2.x, which removed ``mcp.server.fastmcp``;
- that failure was reported as "package not installed", sending users into
  a ``pip install`` loop against an already-satisfied requirement;
- docs advertised console scripts and CLI flags that do not exist.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

from sillok.naru import router_2tier

REPO_ROOT = Path(__file__).resolve().parents[2]


def _pyproject() -> dict:
    return tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))


# --------------------------------------------------------------------------
# packaging
# --------------------------------------------------------------------------

def test_wheel_bundles_the_pack_registry() -> None:
    """packs/ must be force-included, or an installed wheel has no registry."""
    force_include = (
        _pyproject()["tool"]["hatch"]["build"]["targets"]["wheel"]
        .get("force-include", {})
    )
    assert force_include.get("packs") == "sillok/_packs", (
        "packs/ is not bundled into the wheel — load_registry() would then "
        "only work when cwd happens to be a Sillok checkout"
    )


def test_mcp_extra_excludes_sdk_2x() -> None:
    """MCP SDK 2.0 removed mcp.server.fastmcp — the extra must exclude it."""
    extras = _pyproject()["project"]["optional-dependencies"]["mcp"]
    spec = next(s for s in extras if s.startswith("mcp"))
    assert "<2" in spec, f"unbounded mcp requirement {spec!r} resolves to 2.x"


def test_only_the_sillok_console_script_is_declared() -> None:
    """Docs must not promise sillok-mcp / sillok-tongsa entry points."""
    assert set(_pyproject()["project"]["scripts"]) == {"sillok"}


# --------------------------------------------------------------------------
# registry resolution
# --------------------------------------------------------------------------

def test_resolve_registry_prefers_explicit_path(tmp_path: Path) -> None:
    explicit = tmp_path / "custom.yaml"
    explicit.write_text("packs: []\n", encoding="utf-8")
    assert router_2tier.resolve_registry(explicit) == explicit


def test_resolve_registry_honours_env_var(tmp_path: Path, monkeypatch) -> None:
    target = tmp_path / "registry.yaml"
    target.write_text("packs: []\n", encoding="utf-8")
    monkeypatch.setenv(router_2tier.REGISTRY_ENV_VAR, str(target))
    assert router_2tier.resolve_registry() == target


def test_resolve_registry_prefers_cwd_checkout_over_env_miss(
    tmp_path: Path, monkeypatch
) -> None:
    """A stale env var must not shadow a real checkout."""
    checkout = tmp_path / "packs"
    checkout.mkdir()
    (checkout / "registry.yaml").write_text("packs: []\n", encoding="utf-8")
    monkeypatch.setenv(router_2tier.REGISTRY_ENV_VAR, str(tmp_path / "gone.yaml"))
    monkeypatch.chdir(tmp_path)
    assert router_2tier.resolve_registry() == checkout / "registry.yaml"


def test_missing_registry_error_lists_what_was_tried(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.delenv(router_2tier.REGISTRY_ENV_VAR, raising=False)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(router_2tier, "bundled_registry", lambda: None)
    with pytest.raises(FileNotFoundError) as excinfo:
        router_2tier.resolve_registry()
    message = str(excinfo.value)
    assert str(tmp_path) in message, "error must name the cwd it looked in"
    assert router_2tier.REGISTRY_ENV_VAR in message, "error must name the escape hatch"


def test_pack_bodies_resolve_next_to_their_registry(tmp_path: Path, monkeypatch) -> None:
    """A bundled registry must find bundled bodies, not ./packs under cwd."""
    bundle = tmp_path / "_packs"
    (bundle / "methodology").mkdir(parents=True)
    (bundle / "registry.yaml").write_text("packs: []\n", encoding="utf-8")
    body = bundle / "methodology" / "pm.md"
    body.write_text("# body\n", encoding="utf-8")

    monkeypatch.setattr(
        router_2tier, "resolve_registry", lambda path=None: bundle / "registry.yaml"
    )
    assert router_2tier.resolve_pack_body("packs/methodology/pm.md") == body


# --------------------------------------------------------------------------
# MCP bridge diagnostics
# --------------------------------------------------------------------------

def test_incompatible_mcp_is_not_reported_as_missing() -> None:
    """The 'already satisfied' loop: a present-but-wrong SDK must say so."""
    pytest.importorskip("mcp")
    from sillok.tongsa import server

    hint = server._mcp_import_hint()
    assert "pip install 'sillok[mcp]'" not in hint, (
        "mcp is importable, so telling the user to install it is a dead end"
    )
    assert "<2" in hint, "hint must name the version constraint that fixes it"


def test_serve_rejects_the_documented_but_nonexistent_stdio_flag() -> None:
    """Docs used to show `--stdio`; the real flag is `--transport stdio`."""
    proc = subprocess.run(
        [sys.executable, "-m", "sillok.tongsa", "serve", "--stdio"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        timeout=60,
    )
    assert proc.returncode != 0
    assert "No such option" in proc.stdout + proc.stderr


# --------------------------------------------------------------------------
# console encoding
# --------------------------------------------------------------------------

def test_cli_survives_a_legacy_windows_code_page() -> None:
    """Sillok prints em dashes; cp949/cp1252 consoles cannot encode them."""
    env = {**os.environ, "PYTHONIOENCODING": "cp949"}
    proc = subprocess.run(
        [sys.executable, "-m", "sillok.tongsa", "describe"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        env=env,
        timeout=60,
    )
    assert proc.returncode == 0, proc.stderr
    assert "UnicodeEncodeError" not in proc.stderr


def test_example_mcp_config_matches_the_real_cli() -> None:
    config = json.loads(
        (REPO_ROOT / "examples" / "claude-code-mcp-config.json").read_text(
            encoding="utf-8"
        )
    )
    server = config["mcpServers"]["sillok"]
    assert server["args"][:2] == ["-m", "sillok.tongsa"]
    assert "--transport" in server["args"] and "stdio" in server["args"]
    assert server["env"]["PYTHONIOENCODING"] == "utf-8"
