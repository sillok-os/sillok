"""Multi-tenant scope overlay — Top 10 Feature #5.

Per-scope overlays let a single registry serve a solo user, a team, and
multiple client engagements without re-architecting. Routing resolves
overlays by precedence: scope-matched > global.

Schema summary:
  - scope: "global" | "client:<id>" | "repo:<id>" | "team:<id>"
  - precedence: scope-aware overlay > global registry
  - file naming: ``packs/registry-overlay-<scope>.yaml``

Activation: opt-in via ``--scope`` flag on the router (``sillok route --scope
client:acme "..."``) or via context-file payload. Overlay files are optional
— if absent, routing falls back to the global registry only.

See ADR 0001 (D5 / D9) and ``sillok/jikji/`` for the registry implementation.
"""
from __future__ import annotations

from typing import Literal

from ._base import BaseModel
from .pack import RegistryPackSchema


ScopeKind = Literal["global", "client", "repo", "team"]


class ScopeIdentifier(BaseModel):
    """Tenant scope identifier — kind + value pair.

    Examples::

        {"kind": "global", "value": ""}
        {"kind": "client", "value": "acme"}
        {"kind": "repo",   "value": "vault"}
        {"kind": "team",   "value": "consulting"}
    """

    kind: ScopeKind
    value: str = ""

    def render(self) -> str:
        """Canonical string form: 'global' or '<kind>:<value>'."""
        if self.kind == "global":
            return "global"
        return f"{self.kind}:{self.value}"


class RegistryOverlay(BaseModel):
    """Per-scope overlay — adds, modifies, or hides packs.

    Resolution order at routing time (highest priority first):

      1. scope-matched overlay's ``add`` packs
      2. scope-matched overlay's ``override`` packs (replaces global by id)
      3. global registry packs (excluding ``hide`` list from overlay)
      4. (no match → fall back to global only)

    File location: ``packs/registry-overlay-<scope-render>.yaml``
                   e.g. ``packs/registry-overlay-client-acme.yaml``
    """

    version: str
    scope: ScopeIdentifier
    description: str = ""
    add: list[RegistryPackSchema] = []          # new packs only in this scope
    override: list[RegistryPackSchema] = []     # replaces global pack with same id
    hide: list[str] = []                        # pack ids hidden in this scope


def merge_with_global(
    overlay: RegistryOverlay | None,
    global_packs: list[RegistryPackSchema],
) -> list[RegistryPackSchema]:
    """Merge a scope overlay with the global registry packs.

    Behaviour when overlay is None: returns ``global_packs`` unchanged.
    Conflict resolution: override > global (by ``id``).
    """
    if overlay is None:
        return list(global_packs)

    by_id: dict[str, RegistryPackSchema] = {p.id: p for p in global_packs}

    # 1) hide
    for hidden in overlay.hide:
        by_id.pop(hidden, None)

    # 2) override (replaces existing by id)
    for op in overlay.override:
        by_id[op.id] = op

    # 3) add (new packs)
    for ap in overlay.add:
        if ap.id not in by_id:
            by_id[ap.id] = ap

    return list(by_id.values())


__all__ = ["ScopeIdentifier", "RegistryOverlay", "merge_with_global"]
