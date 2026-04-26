"""Polling watcher for Phase 0 bootstrap of Top 10 Feature #1.

This is a deliberately minimal watcher with **no external dependencies**:
it polls every ``interval`` seconds, recomputes a directory signature, and
calls :func:`ingest_md` when anything changed.

PR-K (Phase 2) replaces this with fswatch (macOS) / inotify (Linux)
event-based triggers, sub-second latency, and incremental indexing.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import signal
import sys
import time
from pathlib import Path

from .ingest_md import DEFAULT_EXCLUDES, ingest_md

DEFAULT_INTERVAL = 5.0  # seconds


def _vault_signature(vault: Path, excludes: tuple[str, ...]) -> str:
    """Stable signature over (path, mtime, size) of every md file."""
    h = hashlib.sha256()
    for root, dirs, files in os.walk(vault):
        dirs[:] = [d for d in dirs if d not in excludes]
        files.sort()
        for name in files:
            if not name.endswith(".md"):
                continue
            fp = Path(root) / name
            try:
                stat = fp.stat()
            except OSError:
                continue
            h.update(str(fp.relative_to(vault)).encode("utf-8"))
            h.update(str(stat.st_mtime).encode("utf-8"))
            h.update(str(stat.st_size).encode("utf-8"))
    return h.hexdigest()


def watch_md(
    vault: Path,
    *,
    interval: float = DEFAULT_INTERVAL,
    excludes: tuple[str, ...] = DEFAULT_EXCLUDES,
    once: bool = False,
) -> None:
    """Poll the vault and re-ingest on change. Blocking call.

    Args:
        vault: vault root.
        interval: seconds between polls.
        excludes: directory names to skip.
        once: if True, run a single poll cycle (useful in tests).

    Stops cleanly on SIGINT / SIGTERM.
    """
    vault = vault.resolve()
    stop = {"flag": False}

    def _handle_signal(*_args: object) -> None:
        stop["flag"] = True

    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    last_sig = ""
    cycles = 0
    while not stop["flag"]:
        sig = _vault_signature(vault, excludes)
        if sig != last_sig:
            t0 = time.time()
            n = ingest_md(vault, excludes=excludes)
            elapsed = time.time() - t0
            print(
                f"watcher: {n} md files re-indexed in {elapsed:.2f}s",
                file=sys.stderr,
            )
            last_sig = sig
        cycles += 1
        if once:
            break
        time.sleep(interval)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "vault",
        type=Path,
        help="vault root to watch",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=DEFAULT_INTERVAL,
        help=f"poll interval in seconds (default {DEFAULT_INTERVAL})",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="additional directories to exclude (repeatable)",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="run a single poll cycle and exit (testing)",
    )
    args = parser.parse_args(argv)

    excludes = tuple(list(DEFAULT_EXCLUDES) + list(args.exclude))
    watch_md(args.vault, interval=args.interval, excludes=excludes, once=args.once)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
