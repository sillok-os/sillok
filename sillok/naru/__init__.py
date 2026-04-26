"""sillok.naru — Two-Stage Routing (Top 10 Feature #2).

Public API:

  - :func:`tier1_match`     — Tier 1 keyword/regex match across packs
  - :func:`tier2_load_full` — Tier 2 full-body load for selected candidates
  - :func:`tier_breakdown`  — distribution of discovery_tier across registry
  - :func:`load_registry`   — read ``packs/registry.yaml``
  - :func:`shadow_dump`     — persist routing result for offline comparison
  - :func:`discovery_tier`  — heuristic when pack lacks explicit declaration

CLI: ``python -m sillok.naru.router_2tier --help``
"""
from __future__ import annotations

from .router_2tier import (
    discovery_tier,
    load_registry,
    shadow_dump,
    tier1_match,
    tier2_load_full,
    tier_breakdown,
)

__all__ = [
    "discovery_tier",
    "load_registry",
    "shadow_dump",
    "tier1_match",
    "tier2_load_full",
    "tier_breakdown",
]
