"""Per-session kernel state: hashed file names, atomic JSON writes, a lock.

Shared by the work-context (``sacho``), context-budget (``seungjeongwon``)
and playbook (``gyeongyeon``) managers so that all three keep their state
side by side under one directory::

    <state_dir>/<session_hash>.json            work context
    <state_dir>/<session_hash>.budget.json     context budget (seen blocks)
    <state_dir>/<session_hash>.playbook.json   playbook exposure + counted keys
    <state_dir>/_playbook.json                 global playbook (never pruned)

Raw session IDs are never written — only a 16-hex SHA-256 prefix. Every
reader treats a missing or corrupt file as "no state": kernel state is an
optimisation and must never block a turn.
"""

from __future__ import annotations

import contextlib
import hashlib
import json
import os
import re
import tempfile
import time
from pathlib import Path
from typing import Any

PRUNE_AFTER_S = 7 * 86400
PRUNE_WHEN_FILES = 200
_SESSION_FILE = re.compile(r"^[0-9a-f]{16}(\.[a-z]+)?\.json$")


def session_hash(session_id: str) -> str:
    """16-hex SHA-256 prefix of a session ID ('' for an empty ID)."""
    value = (session_id or "").strip()
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16] if value else ""


def session_file(state_dir: Path, session_id: str, kind: str = "") -> Path:
    """``<state_dir>/<hash>[.<kind>].json`` for a session."""
    suffix = f".{kind}.json" if kind else ".json"
    return Path(state_dir) / f"{session_hash(session_id)}{suffix}"


def read_json(path: Path) -> dict[str, Any]:
    """Return the JSON object at ``path``, or ``{}`` if absent/corrupt/not an object."""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def write_json_atomic(path: Path, data: dict[str, Any]) -> None:
    """Write via a temp file + ``os.replace`` so readers never see half a file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=f".{path.stem}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def prune(state_dir: Path, now: float | None = None) -> None:
    """Delete session files idle for 7 days, at most once a day, only past 200 files.

    Global files (``_playbook.json``) never match the session-file pattern
    and are never pruned.
    """
    folder = Path(state_dir)
    stamp = folder / ".prune-stamp"
    now = time.time() if now is None else now
    try:
        if stamp.exists() and now - stamp.stat().st_mtime < 86400:
            return
        folder.mkdir(parents=True, exist_ok=True)
        stamp.touch()
        files = [p for p in folder.glob("*.json") if _SESSION_FILE.match(p.name)]
        if len(files) <= PRUNE_WHEN_FILES:
            return
        cutoff = now - PRUNE_AFTER_S
        for path in files:
            if path.stat().st_mtime < cutoff:
                path.unlink(missing_ok=True)
                path.with_suffix(".lock").unlink(missing_ok=True)
    except OSError:
        pass


class FileLock:
    """Exclusive, non-blocking-with-deadline lock on a lock file.

    POSIX ``flock`` or Windows ``msvcrt.locking``; the OS releases both when
    the holder exits, so there is no path that steals a live lock because it
    looks old. If the lock is not acquired within ``wait_s`` (or no locking
    primitive exists) ``held`` stays False and callers must not write —
    failing towards "don't save" rather than "save over someone else".
    """

    def __init__(self, path: Path, wait_s: float = 0.5) -> None:
        self.path = Path(path)
        self.wait_s = wait_s
        self.held = False
        self._fh: Any = None
        self._msvcrt: Any = None

    def _try(self) -> bool:
        try:
            import fcntl
        except ImportError:
            fcntl = None  # type: ignore[assignment]
        if fcntl is not None:
            try:
                fcntl.flock(self._fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                return False
            return True
        import msvcrt  # type: ignore[import-not-found,unused-ignore]  # Windows

        try:
            self._fh.seek(0)
            msvcrt.locking(self._fh.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError:
            return False
        self._msvcrt = msvcrt
        return True

    def __enter__(self) -> FileLock:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self._fh = open(self.path, "a+")  # noqa: SIM115 — closed in __exit__
            deadline = time.monotonic() + self.wait_s
            while True:
                if self._try():
                    self.held = True
                    break
                if time.monotonic() > deadline:
                    break
                time.sleep(0.01)
        except (OSError, ImportError):
            self.held = False
        return self

    def __exit__(self, *exc: object) -> None:
        if self._fh is None:
            return
        if self.held and self._msvcrt is not None:
            with contextlib.suppress(OSError):
                self._fh.seek(0)
                self._msvcrt.locking(self._fh.fileno(), self._msvcrt.LK_UNLCK, 1)
        with contextlib.suppress(OSError):
            self._fh.close()


def session_lock(state_dir: Path, session_id: str, wait_s: float = 0.5) -> FileLock:
    return FileLock(Path(state_dir) / f"{session_hash(session_id)}.lock", wait_s)


def env_off(name: str) -> bool:
    """True when environment variable ``name`` is set to off/0/false."""
    return os.environ.get(name, "").strip().lower() in {"off", "0", "false"}
