"""sillok.pyeonchan — Multi-format Auto-Ingest (Top 10 Feature #1).

Phase 0 bootstrap covers ``md`` only with a polling-based watcher.

Public API:

  - :func:`ingest_md`  — walk a vault and write ``.sillok-janggyeong/index.jsonl``
  - :func:`watch_md`   — polling watcher that calls :func:`ingest_md` on change
  - :func:`Atom`       — lightweight in-memory representation of an indexed file

PR-K (Phase 2) extends this to ``pdf`` / ``docx`` / ``xlsx`` / ``pptx`` /
``txt`` / ``hwpx`` formats and adds fswatch / inotify / cron triggers.
"""
from __future__ import annotations

from .ingest_md import Atom, ingest_md
from .watcher import watch_md

__all__ = ["Atom", "ingest_md", "watch_md"]
