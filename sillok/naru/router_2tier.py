"""sillok.naru.router_2tier — Two-stage routing (Top 10 Feature #2).

Tier 1 (summary): load every pack's ``trigger_signals`` + ``summary_overlay``
                  → select top-K candidates
Tier 2 (full):    load full body (``.md``) of selected top-K packs
                  → final composition

Token economy (typical, 56 packs × ~4KB body)::

    naive load:  56 × 4 KB                        =  224 KB
    2-tier:      56 × 100 B summary + K × 4 KB    =   25 KB
    saving:      ~88%

Heuristic ``discovery_tier`` (when not declared in the pack):

  - ``last_used_12d >= 5`` OR ``precedence >= 90``  →  ``full``
  - otherwise                                       →  ``summary``

CLI usage::

    python -m sillok.naru.router_2tier --message "<msg>" --tier full
    python -m sillok.naru.router_2tier --message "<msg>" --tier summary
    python -m sillok.naru.router_2tier --message "<msg>" --top-k 5

Shadow mode (parallel run + result dump for cutover comparison)::

    python -m sillok.naru.router_2tier --shadow --message "<msg>"

Governance: proposal-only. This module does not replace the v2 router; in
shadow mode it runs in parallel and dumps results for offline diff before
cutover.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

# Defaults are relative to the current working directory; override via
# environment variables or pass explicit Path arguments to the helper
# functions below for testability.
DEFAULT_REGISTRY = Path("packs") / "registry.yaml"
DEFAULT_SHADOW_DIR = Path(".sillok") / "shadow-2tier"


def load_registry(registry_path: Path = DEFAULT_REGISTRY) -> list[dict[str, Any]]:
    """Load and return the packs list from ``packs/registry.yaml``."""
    payload = yaml.safe_load(registry_path.read_text(encoding="utf-8")) or {}
    return payload.get("packs", []) or []


def discovery_tier(pack: dict[str, Any]) -> str:
    """Heuristic for packs without explicit ``discovery_tier`` declaration."""
    if pack.get("discovery_tier") in ("summary", "full"):
        return pack["discovery_tier"]
    if (pack.get("last_used_12d") or 0) >= 5:
        return "full"
    if (pack.get("precedence") or 0) >= 90:
        return "full"
    return "summary"


def tier1_match(
    message: str,
    packs: list[dict[str, Any]],
    top_k: int = 5,
) -> list[dict[str, Any]]:
    """Tier 1: select candidates via ``trigger_signals`` + ``summary_overlay``."""
    msg_lower = message.lower()
    candidates: list[dict[str, Any]] = []
    for pack in packs:
        if pack.get("status") in ("archived",):
            continue
        sig = pack.get("trigger_signals") or {}
        score = 0.0
        reasons: list[str] = []

        # Explicit triggers (highest weight)
        for explicit in sig.get("explicit", []) or []:
            if explicit.lower() in msg_lower:
                score += 200
                reasons.append(f"explicit:{explicit}")

        # Contains keywords
        matches: list[str] = []
        for kw in sig.get("contains", []) or []:
            if not kw:
                continue
            if kw.lower() in msg_lower:
                matches.append(kw)
                score += 25
        if matches:
            reasons.append(f"keyword:{','.join(matches[:5])}")

        # Precedence as tie-breaker (10% weight)
        score += (pack.get("precedence") or 0) * 0.1

        if score > 0:
            candidates.append(
                {
                    "pack_id": pack["id"],
                    "score": round(score, 2),
                    "reasons": reasons,
                    "tier": discovery_tier(pack),
                    "category": pack.get("category"),
                    "summary_overlay": pack.get("summary_overlay") or [],
                }
            )
    candidates.sort(key=lambda x: -x["score"])
    return candidates[:top_k]


def tier2_load_full(
    candidates: list[dict[str, Any]],
    packs: list[dict[str, Any]],
    repo_root: Path = Path.cwd(),
) -> dict[str, Any]:
    """Tier 2: load body of selected candidates and account for token cost."""
    pack_index = {p["id"]: p for p in packs}
    full_loaded: dict[str, dict[str, Any]] = {}
    total_chars = 0
    for c in candidates:
        pack = pack_index.get(c["pack_id"])
        if not pack:
            continue
        body_path = repo_root / pack["path"]
        if not body_path.exists():
            full_loaded[c["pack_id"]] = {"loaded": False, "reason": "missing"}
            continue
        body = body_path.read_text(encoding="utf-8")
        total_chars += len(body)
        full_loaded[c["pack_id"]] = {
            "loaded": True,
            "char_count": len(body),
            "approx_tokens": len(body) // 4,
        }
    return {
        "loaded_packs": full_loaded,
        "total_chars": total_chars,
        "approx_tokens": total_chars // 4,
    }


def tier_breakdown(
    packs: list[dict[str, Any]],
    repo_root: Path = Path.cwd(),
) -> dict[str, Any]:
    """Distribution of ``discovery_tier`` across all packs (for capacity planning)."""
    counts = {"summary": 0, "full": 0}
    summary_chars, full_chars = 0, 0
    for p in packs:
        t = discovery_tier(p)
        counts[t] += 1
        body_path = repo_root / p["path"]
        if body_path.exists():
            sz = body_path.stat().st_size
            if t == "summary":
                summary_chars += sz
            else:
                full_chars += sz
    return {
        "tier_counts": counts,
        "summary_total_chars": summary_chars,
        "full_total_chars": full_chars,
        "tier1_load_chars_estimate": sum(
            sum(len(s) for s in (p.get("summary_overlay") or [])) + 200
            for p in packs
        ),
    }


def shadow_dump(
    message: str,
    result_2tier: dict[str, Any],
    shadow_dir: Path = DEFAULT_SHADOW_DIR,
) -> Path:
    """Persist a 2-tier routing result for shadow-mode comparison."""
    shadow_dir.mkdir(parents=True, exist_ok=True)
    h = hashlib.sha256(message.encode()).hexdigest()[:16]
    path = shadow_dir / f"{datetime.now().strftime('%Y%m%d')}-{h}.json"
    path.write_text(
        json.dumps(
            {
                "message": message[:500],
                "router": "2tier",
                "result": result_2tier,
                "timestamp": datetime.now().isoformat(),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("--message", required=False, help="message to route")
    parser.add_argument(
        "--tier",
        choices=["summary", "full"],
        default="full",
        help="summary = tier1 only / full = tier1 + tier2 (default)",
    )
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument(
        "--shadow",
        action="store_true",
        help="dump result into .sillok/shadow-2tier/",
    )
    parser.add_argument(
        "--breakdown",
        action="store_true",
        help="show tier distribution only (no message required)",
    )
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--registry",
        type=Path,
        default=DEFAULT_REGISTRY,
        help="path to packs/registry.yaml",
    )
    args = parser.parse_args(argv)

    packs = load_registry(args.registry)

    if args.breakdown:
        bd = tier_breakdown(packs)
        if args.json:
            print(json.dumps(bd, indent=2))
        else:
            print(f"2-tier breakdown ({len(packs)} packs)")
            print(
                f"   summary: {bd['tier_counts']['summary']} packs "
                f"({bd['summary_total_chars']:>8,} chars)"
            )
            print(
                f"   full:    {bd['tier_counts']['full']} packs "
                f"({bd['full_total_chars']:>8,} chars)"
            )
            total = bd["summary_total_chars"] + bd["full_total_chars"]
            print(f"   total body chars: {total:,}")
            print(f"   tier1 load estimate: {bd['tier1_load_chars_estimate']:,} chars")
            saving_pct = 100 * (1 - bd["tier1_load_chars_estimate"] / max(total, 1))
            print(f"   estimated saving: {saving_pct:.1f}%")
        return 0

    if not args.message:
        print("--message required (or use --breakdown)", file=sys.stderr)
        return 1

    # Tier 1
    candidates = tier1_match(args.message, packs, top_k=args.top_k)
    result: dict[str, Any] = {
        "router": "2tier",
        "tier": args.tier,
        "tier1_candidates": candidates,
    }

    # Tier 2 if requested
    if args.tier == "full":
        result["tier2"] = tier2_load_full(candidates, packs)

    if args.shadow:
        path = shadow_dump(args.message, result)
        result["shadow_path"] = str(path)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"2-tier router — '{args.message[:60]}'")
        print(f"   tier1 candidates ({len(candidates)}):")
        for c in candidates:
            reason = c["reasons"][0] if c["reasons"] else ""
            print(
                f"     [{c['tier']:>7}] {c['pack_id']:35s} "
                f"score={c['score']:>6.1f}  {reason}"
            )
        if args.tier == "full":
            t2 = result["tier2"]
            print("   tier2 loaded:")
            for pid, info in t2["loaded_packs"].items():
                if info.get("loaded"):
                    print(f"     OK  {pid:35s} ~{info['approx_tokens']:>5} tokens")
                else:
                    print(f"     --  {pid:35s} {info.get('reason')}")
            print(f"   total tier2 tokens: ~{t2['approx_tokens']:,}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
