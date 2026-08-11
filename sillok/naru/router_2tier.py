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
import os
import sys
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any

import yaml

from sillok._console import enable_utf8_console

# Registry resolution order (see :func:`resolve_registry`):
#   explicit argument > $SILLOK_REGISTRY > ./packs/registry.yaml > bundled
# ``DEFAULT_REGISTRY`` stays for backwards compatibility — it names the
# in-repo location only, and is no longer the sole lookup path.
DEFAULT_REGISTRY = Path("packs") / "registry.yaml"
DEFAULT_SHADOW_DIR = Path(".sillok") / "shadow-2tier"

#: Env var pointing at a registry.yaml — set this when Sillok runs with a
#: working directory that is not a Sillok checkout (MCP servers, IDE
#: plugins and cron jobs all inherit the *host's* cwd, not Sillok's).
REGISTRY_ENV_VAR = "SILLOK_REGISTRY"


def bundled_registry() -> Path | None:
    """Return the registry shipped inside the installed wheel, if present."""
    candidate = Path(__file__).resolve().parent.parent / "_packs" / "registry.yaml"
    return candidate if candidate.is_file() else None


def resolve_registry(registry_path: Path | None = None) -> Path:
    """Resolve which ``registry.yaml`` to read.

    Order: explicit argument > ``$SILLOK_REGISTRY`` > ``./packs/registry.yaml``
    (a Sillok checkout as cwd) > the copy bundled in the installed wheel.

    Raises:
        FileNotFoundError: when no registry can be located, with the full
            list of paths tried — a bare ``packs/registry.yaml`` message
            is unactionable for anyone running outside a checkout.
    """
    if registry_path is not None:
        return Path(registry_path)

    tried: list[str] = []

    from_env = os.environ.get(REGISTRY_ENV_VAR)
    if from_env:
        env_path = Path(from_env)
        if env_path.is_file():
            return env_path
        tried.append(f"${REGISTRY_ENV_VAR}={from_env}")

    cwd_path = Path.cwd() / DEFAULT_REGISTRY
    if cwd_path.is_file():
        return cwd_path
    tried.append(str(cwd_path))

    bundled = bundled_registry()
    if bundled is not None:
        return bundled
    tried.append("<bundled sillok/_packs/registry.yaml — not in this install>")

    raise FileNotFoundError(
        "No Sillok pack registry found. Tried:\n  - "
        + "\n  - ".join(tried)
        + f"\nFix: set {REGISTRY_ENV_VAR}=/path/to/packs/registry.yaml, or run "
        "from a Sillok checkout, or reinstall a wheel that bundles the packs "
        "(pip install --pre --force-reinstall 'sillok[mcp]')."
    )


def load_registry(registry_path: Path | None = None) -> list[dict[str, Any]]:
    """Load and return the packs list from the resolved registry."""
    resolved = resolve_registry(registry_path)
    payload = yaml.safe_load(resolved.read_text(encoding="utf-8")) or {}
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


def resolve_pack_body(pack_path: str, repo_root: Path | None = None) -> Path:
    """Resolve a registry ``path`` entry to a pack body on disk.

    Registry entries are written repo-relative (``packs/<sub>/<id>.md``).
    When ``repo_root`` is omitted the path is resolved against whichever
    registry :func:`resolve_registry` picked, so a wheel-bundled registry
    at ``sillok/_packs/registry.yaml`` finds ``sillok/_packs/<sub>/<id>.md``
    instead of looking for a ``packs/`` directory under the caller's cwd.
    """
    rel = PurePosixPath(pack_path)
    if repo_root is not None:
        return repo_root / Path(*rel.parts)

    registry_dir = resolve_registry().parent
    if rel.parts and rel.parts[0] == "packs":
        return registry_dir.joinpath(*rel.parts[1:])
    return registry_dir.parent.joinpath(*rel.parts)


def tier2_load_full(
    candidates: list[dict[str, Any]],
    packs: list[dict[str, Any]],
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Tier 2: load body of selected candidates and account for token cost."""
    pack_index = {p["id"]: p for p in packs}
    full_loaded: dict[str, dict[str, Any]] = {}
    total_chars = 0
    for c in candidates:
        pack = pack_index.get(c["pack_id"])
        if not pack:
            continue
        body_path = resolve_pack_body(pack["path"], repo_root)
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
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Distribution of ``discovery_tier`` across all packs (for capacity planning)."""
    counts = {"summary": 0, "full": 0}
    summary_chars, full_chars = 0, 0
    for p in packs:
        t = discovery_tier(p)
        counts[t] += 1
        body_path = resolve_pack_body(p["path"], repo_root)
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
        default=None,
        help=(
            "path to packs/registry.yaml "
            f"(default: ${REGISTRY_ENV_VAR} > ./packs/registry.yaml > bundled)"
        ),
    )
    args = parser.parse_args(argv)

    enable_utf8_console()

    try:
        packs = load_registry(args.registry)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 2

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
