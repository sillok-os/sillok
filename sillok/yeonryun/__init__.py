"""sillok.yeonryun — auto-growth / knowledge promotion loop.

The *promotion* half of the auto-growth loop. ``yeonryun.disposition``
scores research / result documents for reusability and decides whether
each one should:

  - stay in place (``none``)
  - be absorbed into the local repo (``local-reusable``)
  - be promoted to the shared vault as one or more atomic notes
    (``cross-repo-reusable``)

The *retrieval* half — searching what has already been promoted —
lives in :mod:`sillok.bongsu`.

Public API mirrors :mod:`sillok.yeonryun.disposition` so callers can
import the high-traffic helpers directly from the package root.
"""
from __future__ import annotations

from .disposition import (
    CROSS_REPO_THRESHOLD,
    EPHEMERAL_PATTERNS,
    LOCAL_THRESHOLD,
    MIN_CONTENT_LENGTH,
    REUSABLE_PATTERNS,
    determine_disposition,
    extract_body,
    format_report,
    generate_atomic_note,
    identify_extractable_atoms,
    parse_frontmatter,
    process_file,
    scan_directory,
    score_reusability,
)

__all__ = [
    "CROSS_REPO_THRESHOLD",
    "EPHEMERAL_PATTERNS",
    "LOCAL_THRESHOLD",
    "MIN_CONTENT_LENGTH",
    "REUSABLE_PATTERNS",
    "determine_disposition",
    "extract_body",
    "format_report",
    "generate_atomic_note",
    "identify_extractable_atoms",
    "parse_frontmatter",
    "process_file",
    "scan_directory",
    "score_reusability",
]
