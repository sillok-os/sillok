"""sillok.bongsu — Five Retrieval Plans (Top 10 Feature #3).

Public API:

  - :func:`patch_telemetry` — fill in retrieval-side fields on a routed
    telemetry row after the configured plan has executed
  - :func:`load_hits`       — convert a corpus query JSON output to the
    hit-summary dict expected by :func:`patch_telemetry`

The five retrieval plans themselves (``vault_first``,
``vault_then_llmwiki_fallback``, ``llmwiki_recovery_first``,
``dual_compare``, ``no_corpus``) are declared per-pack in
``packs/registry.yaml`` and resolved by ``sillok.naru`` at routing time.
This module provides the post-execution telemetry loop only.
"""
from __future__ import annotations

from .post_update import _load_hits as load_hits
from .post_update import patch_telemetry

__all__ = ["patch_telemetry", "load_hits"]
