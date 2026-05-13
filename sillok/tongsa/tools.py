"""sillok.tongsa.tools — pure tool functions exposed over MCP.

These functions are *pure* and importable without the optional ``mcp``
package — that lets the routing logic + reason-code mapping be unit-tested
without a running MCP server. The FastMCP binding lives in
``sillok.tongsa.server``.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from sillok.naru.router_2tier import load_registry, tier1_match


# Reason codes tagged on every routing decision.
# These mirror what the README claims ("R1~R7 audit-ready").
REASON_CODES: dict[str, str] = {
    "R1": "explicit-trigger match (highest weight)",
    "R2": "keyword contains match",
    "R3": "precedence tie-break (10% weight)",
    "R4": "discovery_tier full elevation (precedence ≥ 90)",
    "R5": "discovery_tier full elevation (last_used_12d ≥ 5)",
    "R6": "top-K cutoff — candidate truncated below cut-line",
    "R7": "empty-candidate fallback — no triggers matched any pack",
}


# ---------------------------------------------------------------------------
# sillok.list_packs
# ---------------------------------------------------------------------------

def sillok_list_packs(
    registry_path: Path | None = None,
) -> list[dict[str, Any]]:
    """Return a compact summary of every registered pack.

    Args:
        registry_path: optional override for ``packs/registry.yaml``.

    Returns:
        list of dicts with keys: ``id``, ``title``, ``category``,
        ``sub_category``, ``precedence``, ``visibility_label``,
        ``capabilities`` (if v0.9 frontmatter present in pack body).
    """
    packs = load_registry(registry_path) if registry_path else load_registry()
    return [
        {
            "id": pack.get("id"),
            "title": pack.get("title"),
            "category": pack.get("category"),
            "sub_category": pack.get("sub_category"),
            "precedence": pack.get("precedence", 0),
            "visibility_label": pack.get("visibility_label"),
            "summary_overlay": pack.get("summary_overlay") or [],
            "intent_tags": pack.get("intent_tags") or [],
            "output_contracts": pack.get("output_contracts") or [],
        }
        for pack in packs
    ]


# ---------------------------------------------------------------------------
# sillok.route
# ---------------------------------------------------------------------------

def sillok_route(
    message: str,
    top_k: int = 3,
    registry_path: Path | None = None,
) -> dict[str, Any]:
    """Tier-1 route a natural-language message to top-K packs.

    Args:
        message: the user's request.
        top_k: how many top candidates to return (default 3).
        registry_path: optional override for ``packs/registry.yaml``.

    Returns:
        dict with keys ``packs`` (list of candidate dicts) and
        ``reason_codes`` (list of R1-R7 strings explaining the routing).
    """
    packs = load_registry(registry_path) if registry_path else load_registry()
    candidates = tier1_match(message, packs, top_k=top_k)
    # The router's tier1_match returns precedence-only matches (score == 0
    # before precedence boost) — for the MCP API, "no trigger matched" should
    # produce an empty result with R7, not a noisy precedence-only ranking.
    candidates = [c for c in candidates if c.get("reasons")]
    if not candidates:
        return {
            "packs": [],
            "reason_codes": ["R7"],
        }

    enriched: list[dict[str, Any]] = []
    seen_codes: list[str] = []
    for cand in candidates:
        codes = classify_reason_codes(cand)
        for c in codes:
            if c not in seen_codes:
                seen_codes.append(c)
        enriched.append(
            {
                "pack_id": cand["pack_id"],
                "score": cand["score"],
                "reasons": cand["reasons"],
                "reason_codes": codes,
                "tier": cand["tier"],
                "category": cand.get("category"),
            }
        )

    # R6 only when the router truncated *real* matches (not precedence-only).
    # We pre-filtered precedence-only above, so any time we returned exactly
    # top_k candidates from a registry of more packs, the truncation was real.
    if len(packs) > top_k and len(enriched) >= top_k:
        seen_codes.append("R6")

    return {
        "packs": enriched,
        "reason_codes": seen_codes,
    }


# ---------------------------------------------------------------------------
# sillok.search
# ---------------------------------------------------------------------------

def sillok_search(
    query: str,
    vault_path: Path | None = None,
    pack: str | None = None,
    k: int = 5,
) -> list[dict[str, Any]]:
    """Body full-text search across a vault directory.

    Args:
        query: search string (single token or phrase).
        vault_path: directory to scan. Defaults to ``packs/`` so the
            tool is usable in-repo without external setup.
        pack: optional sub_category filter (matches frontmatter
            ``sub_category`` field — useful when the vault contains
            sillok pack bodies).
        k: max results (default 5).

    Returns:
        list of hit dicts with ``path``, ``snippet``, ``frontmatter``.
    """
    from sillok.bongsu.search import (
        extract_body_preview,
        fulltext_search,
        parse_frontmatter,
    )

    root = vault_path or _default_search_root()
    matching = fulltext_search(vault_root=root, search_dirs=(".",), query=query)
    hits: list[dict[str, Any]] = []
    for path_str in sorted(matching)[: k * 2]:  # over-fetch for sub_category filter
        path = Path(path_str)
        if not path.is_absolute():
            path = root / path
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        frontmatter = parse_frontmatter(text) or {}
        if pack and frontmatter.get("sub_category") != pack:
            continue
        hits.append(
            {
                "path": str(path),
                "snippet": extract_body_preview(text, max_lines=8),
                "frontmatter": frontmatter,
            }
        )
        if len(hits) >= k:
            break
    return hits


def _default_search_root() -> Path:
    """Heuristic — packs/ if present, else cwd."""
    cwd = Path.cwd()
    if (cwd / "packs").exists():
        return cwd / "packs"
    return cwd


# ---------------------------------------------------------------------------
# Reason code mapper
# ---------------------------------------------------------------------------

def classify_reason_codes(candidate: dict[str, Any]) -> list[str]:
    """Map a tier1_match candidate's textual reasons to R1-R7 codes.

    Heuristic mapping rules:

    - Any ``explicit:...`` reason  → R1
    - Any ``keyword:...`` reason   → R2
    - Score includes precedence bump (positive, < 200 from explicit) → R3
    - tier == "full" + precedence ≥ 90                              → R4
    - tier == "full" + last_used_12d ≥ 5                             → R5
    """
    reasons = candidate.get("reasons") or []
    codes: list[str] = []
    for reason in reasons:
        if reason.startswith("explicit:"):
            codes.append("R1")
        elif reason.startswith("keyword:"):
            codes.append("R2")

    score = float(candidate.get("score", 0))
    has_explicit = any(c == "R1" for c in codes)
    has_keyword = any(c == "R2" for c in codes)
    if score > 0 and not has_explicit and not has_keyword:
        # No textual reason but still scored — must be precedence-only
        codes.append("R3")
    elif score > 0 and (has_explicit or has_keyword):
        # Score above threshold + explicit/keyword: precedence still contributed
        codes.append("R3")

    tier = candidate.get("tier")
    if tier == "full":
        # We don't know which sub-cause without registry context; emit R4 as
        # the conservative attribution. R5 is added when usage data is available.
        codes.append("R4")

    # Deduplicate while preserving order.
    seen: list[str] = []
    for code in codes:
        if code not in seen:
            seen.append(code)
    return seen
