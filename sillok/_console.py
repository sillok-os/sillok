"""sillok._console — console encoding safety for CLI entry points.

Windows consoles default to the ANSI code page (``cp949`` on Korean
Windows, ``cp1252`` on Western Windows). Sillok's CLI output contains
non-CP characters (em dash ``—``, box drawing ``───``, Korean pack
titles), so any ``print``/``click.echo`` raises::

    UnicodeEncodeError: 'cp949' codec can't encode character '\\u2014'

:func:`enable_utf8_console` re-wraps ``sys.stdout``/``sys.stderr`` in
UTF-8 with ``errors="replace"`` so the CLI degrades to ``?`` instead of
crashing.

This touches only the *text* layer. ``sys.stdout.buffer`` is untouched,
so the MCP stdio transport — which wraps the raw buffer itself — is
unaffected.
"""
from __future__ import annotations

import contextlib
import sys
from typing import IO, Any

_UTF8_ALIASES = {"utf8", "utf-8", "utf_8"}


def enable_utf8_console() -> None:
    """Force UTF-8 on stdout/stderr when the console cannot encode it.

    Idempotent and never raises — a console that refuses reconfiguration
    (redirected pipe, closed stream, embedded host) is left as-is.
    """
    for stream in (sys.stdout, sys.stderr):
        _reconfigure(stream)


def _reconfigure(stream: IO[Any] | None) -> None:
    if stream is None:
        return
    reconfigure = getattr(stream, "reconfigure", None)
    if reconfigure is None:  # not a TextIOWrapper (e.g. StringIO in tests)
        return
    encoding = (getattr(stream, "encoding", "") or "").lower().replace("-", "_")
    if encoding in {alias.replace("-", "_") for alias in _UTF8_ALIASES}:
        return
    # A host that refuses reconfiguration (detached, closed, or non-seekable
    # stream) is left as-is — encoding safety must never break the CLI.
    with contextlib.suppress(ValueError, OSError, AttributeError):
        reconfigure(encoding="utf-8", errors="replace")
