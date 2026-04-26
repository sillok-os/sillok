"""bongsu.post_update — telemetry placeholder fill-in (Top 10 Feature #3).

The router (``sillok.naru``) writes telemetry rows with placeholder fields
(``knowledge_hit_count=null``, ``knowledge_hit_paths=[]``, etc.). This
module patches those placeholders with actual retrieval results AFTER the
configured retrieval plan has run.

Five retrieval plans are supported (declared per-pack in
``packs/registry.yaml``):

  - ``vault_first``                  vault search only
  - ``vault_then_llmwiki_fallback``  vault first, then archived llm-wiki
  - ``llmwiki_recovery_first``       llm-wiki first (historical recovery)
  - ``dual_compare``                 promoted concept + raw provenance
  - ``no_corpus``                    orchestration-only

CLI usage::

    # 1) Router writes a row, you receive corpus_plan in JSON output
    $ sillok route "..." --json > route.json

    # 2) Run the configured retrieval (e.g. vault search)
    $ sillok corpus query --format json > hits.json

    # 3) Patch the telemetry row with actual hit data
    $ python -m sillok.bongsu.post_update \\
        --message-hash "$(jq -r '.input.message_hash // ""' route.json)" \\
        --hits-file hits.json

Outputs:
  - patches the latest matching telemetry row in
    ``.sillok/telemetry.jsonl``
  - rewrites the file atomically (temp + rename)
  - reports which row was updated and what changed
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_TELEMETRY = Path(".sillok") / "telemetry.jsonl"


def _load_hits(path: Path) -> dict[str, Any]:
    """Load corpus retrieval JSON output and convert to a hit summary.

    Expected payload shape (compatible with ``sillok corpus query --format json``)::

        {"hits": [{"path": "...", "tier": "A", "score": 0.83}, ...]}
    """
    payload = json.loads(path.read_text(encoding="utf-8"))
    hits = payload.get("hits") or payload.get("results") or []
    paths = [h.get("path") or h.get("file") or "" for h in hits if h]
    tiers = [h.get("tier", "") for h in hits if h]
    return {
        "knowledge_hit_count": len(paths),
        "knowledge_hit_paths": [p for p in paths if p][:20],
        "knowledge_hit_tiers": [t for t in tiers if t][:20],
    }


def _maybe_promotion_candidate(hits: dict[str, Any], pattern_freq: int) -> bool:
    """Blind-spot detection rule: hit==0 AND same pattern observed >= 3 times."""
    return hits["knowledge_hit_count"] == 0 and pattern_freq >= 3


def _knowledge_gap_label(hits: dict[str, Any]) -> str | None:
    if hits["knowledge_hit_count"] == 0:
        return "no-hits"
    tiers = set(hits.get("knowledge_hit_tiers", []))
    if not tiers - {"D", "E", ""}:
        return "low-tier-only"
    return None


def patch_telemetry(
    telemetry_path: Path,
    *,
    message_hash: str,
    hits: dict[str, Any],
    pattern_freq: int = 0,
    dry_run: bool = False,
) -> tuple[bool, dict[str, Any]]:
    """Find the most recent row matching ``message_hash`` and patch it.

    Returns:
        Tuple of (patched, updated_row). When no row matches or the file
        does not exist, returns ``(False, {})``.
    """
    if not telemetry_path.exists():
        print(f"telemetry not found: {telemetry_path}", file=sys.stderr)
        return False, {}

    rows: list[dict[str, Any]] = []
    target_idx = -1
    with telemetry_path.open(encoding="utf-8") as fh:
        for line in fh:
            stripped = line.rstrip("\n")
            if not stripped:
                continue
            try:
                rows.append(json.loads(stripped))
            except json.JSONDecodeError:
                continue

    # find the most recent matching row
    for i in range(len(rows) - 1, -1, -1):
        if rows[i].get("message_hash") == message_hash:
            target_idx = i
            break

    if target_idx < 0:
        print(f"no row matched message_hash={message_hash}", file=sys.stderr)
        return False, {}

    row = rows[target_idx]
    row["knowledge_hit_count"] = hits["knowledge_hit_count"]
    row["knowledge_hit_paths"] = hits["knowledge_hit_paths"]
    row["knowledge_hit_tiers"] = hits.get("knowledge_hit_tiers", [])
    row["knowledge_gap_label"] = _knowledge_gap_label(hits)
    row["promotion_candidate"] = _maybe_promotion_candidate(hits, pattern_freq)
    row["post_update_at"] = datetime.now(timezone.utc).isoformat()

    if dry_run:
        return True, row

    # atomic rewrite
    fd, tmp = tempfile.mkstemp(
        prefix="telemetry-", suffix=".jsonl", dir=str(telemetry_path.parent)
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as out:
            for r in rows:
                out.write(json.dumps(r, ensure_ascii=False) + "\n")
        os.replace(tmp, telemetry_path)
    except Exception:
        Path(tmp).unlink(missing_ok=True)
        raise
    return True, row


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--message-hash",
        required=True,
        help="sha256 prefix of the original routed message",
    )
    parser.add_argument(
        "--hits-file",
        required=True,
        type=Path,
        help="JSON file with retrieval results (corpus query format)",
    )
    parser.add_argument(
        "--pattern-freq",
        type=int,
        default=0,
        help="How many times this pattern was seen recently (for promotion_candidate)",
    )
    parser.add_argument(
        "--telemetry-file",
        type=Path,
        default=DEFAULT_TELEMETRY,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would change but do not rewrite the file",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON instead of text",
    )
    args = parser.parse_args(argv)

    hits = _load_hits(args.hits_file)
    patched, row = patch_telemetry(
        args.telemetry_file,
        message_hash=args.message_hash,
        hits=hits,
        pattern_freq=args.pattern_freq,
        dry_run=args.dry_run,
    )

    if args.json:
        print(json.dumps({"patched": patched, "row": row}, ensure_ascii=False, indent=2))
    elif patched:
        verb = "would patch" if args.dry_run else "patched"
        print(
            f"{verb}: hash={args.message_hash[:16]}, "
            f"hits={hits['knowledge_hit_count']}, "
            f"gap={row.get('knowledge_gap_label')}, "
            f"promote={row.get('promotion_candidate')}"
        )
    else:
        print("no change")

    return 0 if patched else 2


if __name__ == "__main__":
    raise SystemExit(main())
