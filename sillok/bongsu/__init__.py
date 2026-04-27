"""sillok.bongsu — Five Retrieval Plans (Top 10 Feature #3).

Public API:

  - :func:`build_index`     — scan a vault and return a list of frontmatter dicts
  - :func:`filter_notes`    — apply scope / type / tier / status / topic filters
  - :func:`fulltext_search` — body full-text search (rg -> grep fallback)
  - :func:`patch_telemetry` — fill in retrieval-side fields on a routed
                              telemetry row after the configured plan has executed
  - :func:`load_hits`       — convert a corpus query JSON output to the
                              hit-summary dict expected by :func:`patch_telemetry`
  - :class:`parse_frontmatter`, :func:`extract_body_preview`,
    :func:`canonicalize_scope`, :func:`note_matches_scope` (low-level utilities)

The five retrieval plans themselves (``vault_first``,
``vault_then_llmwiki_fallback``, ``llmwiki_recovery_first``,
``dual_compare``, ``no_corpus``) are declared per-pack in
``packs/registry.yaml`` and resolved by ``sillok.naru`` at routing time.
"""
from __future__ import annotations

from ._common import (
    canonicalize_scope,
    extract_body_preview,
    load_scope_aliases,
    match_field,
    note_matches_scope,
    parse_frontmatter,
)
from .post_update import _load_hits as load_hits
from .post_update import patch_telemetry
from .search import (
    build_index,
    filter_notes,
    format_full,
    format_json,
    format_summary,
    fulltext_search,
    print_stats,
)

__all__ = [
    "build_index",
    "filter_notes",
    "fulltext_search",
    "format_summary",
    "format_full",
    "format_json",
    "print_stats",
    "patch_telemetry",
    "load_hits",
    "parse_frontmatter",
    "extract_body_preview",
    "match_field",
    "canonicalize_scope",
    "note_matches_scope",
    "load_scope_aliases",
]
