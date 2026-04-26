"""Compression configuration schema for context management.

Used by the context compaction utilities (``sillok.cli.compress`` when wired)
for configurable thresholds.
"""
from __future__ import annotations

from ._base import BaseModel, HAS_PYDANTIC


class CompressionConfigSchema(BaseModel):
    """Validation model for context compression configuration."""

    threshold_pct: float = 0.50
    target_tail_pct: float = 0.20
    protect_first_n: int = 3
    protect_last_n: int = 20
    max_tool_result_chars: int = 200


__all__ = [
    "CompressionConfigSchema",
    "HAS_PYDANTIC",
]
