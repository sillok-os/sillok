"""sillok.sacho — work context (kernel manager 1 of 4) · experimental since 0.4.0.

Holds *which kind of work* a session is doing across turns, so short
follow-ups ("go", "continue", a screenshot) keep the guidance of the turn
that named the work. See :mod:`sillok.sacho.context`.

Also owns the per-session state layer (:mod:`sillok.sacho.state`) shared by
the context-budget and playbook managers.
"""

from __future__ import annotations

from .context import decide, match_explicit, path_profile, render_line, replay, resolve, vote
from .state import FileLock, read_json, session_hash, write_json_atomic

__all__ = [
    "FileLock",
    "decide",
    "match_explicit",
    "path_profile",
    "read_json",
    "render_line",
    "replay",
    "resolve",
    "session_hash",
    "vote",
    "write_json_atomic",
]
