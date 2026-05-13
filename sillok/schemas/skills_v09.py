"""sillok.schemas.skills_v09 — agentskills.io v0.9 capability discovery.

Adds an *additive* Pydantic schema for the agentskills.io v0.9 frontmatter
contract used by Cursor / Continue / Codex CLI / ChatGPT Desktop and other
MCP-aware tools for capability discovery.

This schema is additive: a Sillok pack's body may carry both the native
fields (``id`` / ``title`` / ``category`` / ``sub_category`` / ``version`` /
...) and the v0.9 fields (``name`` / ``description`` / ``capabilities`` /
``triggers``) in the same frontmatter block. The router and registry
continue to read native fields only; the v0.9 fields exist for third-party
tool ingestion, not for Sillok's internal routing.

References
----------
- agentskills.io v0.9 spec — capability discovery
- ``adr/0001-initial-architecture-decisions.md`` — design rationale
- Issue #2 — agentskills.io v0.9 capability discovery
"""
from __future__ import annotations

from typing import List

from ._base import BaseModel, Field


class SkillsV09Frontmatter(BaseModel):
    """agentskills.io v0.9 frontmatter contract.

    Fields
    ------
    name
        Stable identifier matching the Sillok pack ``id``. Used by
        capability-discovery clients to address the pack.
    description
        Single-line summary, ≤ 120 characters. Shown verbatim in tool
        pickers — keep it concrete and verb-led.
    capabilities
        List of verb-noun phrases declaring what the pack can do.
        Capability-aware clients ground their tool routing on these
        phrases.
    triggers
        Natural-language phrases (or canonical command tokens like
        ``[pm]``) that signal a user wants this pack. Compatible with the
        native ``trigger_signals`` block in registry.yaml.
    """

    name: str = Field(..., min_length=1, max_length=64)
    description: str = Field(..., min_length=1, max_length=120)
    capabilities: List[str] = Field(default_factory=list)
    triggers: List[str] = Field(default_factory=list)
