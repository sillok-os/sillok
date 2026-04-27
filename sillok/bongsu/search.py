"""bongsu.search — vault-resident corpus search engine.

Sanitized port of the upstream `vault_search.py`. The retrieval engine that
makes the 5 retrieval plans operational. Without it, the plan IDs in
``packs/registry.yaml`` (vault_first / fallback / dual_compare / ...) are
declarations only.

This is the **query** half of the Karpathy LLM Wiki pattern (see Sillok
README §Prior art). The ingest half lives in ``sillok.pyeonchan``.

Two operating modes:

  - **In-memory index** (default): scan vault directories on every call,
    keep notes in a list[dict]. Fast for vaults up to a few thousand
    notes, no external dependency.
  - **Body full-text search**: optional, uses ``ripgrep`` if available;
    falls back to ``grep`` if not; degrades to frontmatter-only filter
    if neither is on PATH.

CLI::

    python -m sillok.bongsu.search --vault ~/Documents/my-vault --stats
    python -m sillok.bongsu.search --vault ~/Documents/my-vault \\
                                    --scope acme --type pattern \\
                                    --query "pricing" --format json
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from ._common import (
    extract_body_preview,
    load_scope_aliases,
    match_field,
    note_matches_scope,
    parse_frontmatter,
)

DEFAULT_SEARCH_DIRS: tuple[str, ...] = (".",)


# ----------------------------------------------------------------------
# Index building
# ----------------------------------------------------------------------


def build_index(
    vault_root: Path,
    search_dirs: tuple[str, ...] | list[str] = DEFAULT_SEARCH_DIRS,
    excludes: tuple[str, ...] = (".git", ".obsidian", ".sillok",
                                 ".sillok-janggyeong", "node_modules",
                                 "__pycache__", ".venv"),
) -> list[dict[str, Any]]:
    """Walk ``vault_root`` (or its named sub-directories) and build a
    list of frontmatter dicts. Every note's ``_path`` and ``_abs_path``
    are populated for downstream formatting.

    Notes without frontmatter are still included with an empty meta dict
    so that body-only searches can find them.
    """
    notes: list[dict[str, Any]] = []
    for sd in search_dirs:
        dir_path = vault_root / sd if sd != "." else vault_root
        if not dir_path.exists():
            continue
        for md_file in dir_path.rglob("*.md"):
            rel_parts = md_file.relative_to(vault_root).parts
            if any(p in excludes for p in rel_parts):
                continue
            try:
                content = md_file.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            meta = parse_frontmatter(content)
            meta["_path"] = str(md_file.relative_to(vault_root))
            meta["_abs_path"] = str(md_file)
            meta["_stem"] = md_file.stem
            notes.append(meta)
    return notes


# ----------------------------------------------------------------------
# Filtering
# ----------------------------------------------------------------------


def filter_notes(
    notes: list[dict[str, Any]],
    *,
    scope: str | None = None,
    note_type: str | None = None,
    tier: str | None = None,
    status: str | None = None,
    topic: str | None = None,
    date_from: str | None = None,
    alias_map: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    """Apply frontmatter filters. Returns a new list."""
    alias_map = alias_map or {}
    result = notes
    if scope:
        result = [n for n in result if note_matches_scope(n, scope, alias_map)]
    if note_type:
        result = [n for n in result if match_field(n, "type", note_type)]
    if tier:
        result = [n for n in result if str(n.get("retrieval_tier", "")).upper() == tier.upper()]
    if status:
        result = [n for n in result if match_field(n, "status", status)]
    if topic:
        result = [
            n for n in result
            if match_field(n, "topic", topic) or match_field(n, "subtopic", topic)
        ]
    if date_from:
        result = [
            n for n in result
            if (n.get("session_date_iso", "") or n.get("date", "") or "") >= date_from
        ]
    return result


# ----------------------------------------------------------------------
# Body full-text search
# ----------------------------------------------------------------------


def fulltext_search(
    vault_root: Path,
    search_dirs: tuple[str, ...] | list[str],
    query: str,
    timeout_seconds: int = 30,
) -> set[str]:
    """Find files whose body matches ``query`` (case-insensitive).

    Uses ``ripgrep`` when available, falls back to ``grep -r``, and
    finally returns an empty set if neither is on PATH.
    """
    matching: set[str] = set()
    for sd in search_dirs:
        dir_path = vault_root / sd if sd != "." else vault_root
        if not dir_path.exists():
            continue
        for cmd in (
            ["rg", "-l", "-i", "--type", "md", query, str(dir_path)],
            ["grep", "-r", "-l", "-i", "--include=*.md", query, str(dir_path)],
        ):
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout_seconds,
                )
            except FileNotFoundError:
                continue
            except subprocess.TimeoutExpired:
                print(
                    f"[bongsu.search] {cmd[0]} timed out ({timeout_seconds}s) — narrow the query",
                    file=sys.stderr,
                )
                return matching
            for line in result.stdout.strip().splitlines():
                if not line:
                    continue
                try:
                    rel = str(Path(line).relative_to(vault_root))
                    matching.add(rel)
                except ValueError:
                    matching.add(line)
            break
    return matching


# ----------------------------------------------------------------------
# Output formatting
# ----------------------------------------------------------------------


def format_summary(notes: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    for i, n in enumerate(notes, 1):
        title = n.get("title", n.get("_stem", "untitled"))
        path = n.get("_path", "")
        tier = n.get("retrieval_tier", "?")
        scope = n.get("scope", "")
        nm_type = n.get("type", "")
        lines.append(f"{i:3d}. [{tier}] {title}")
        lines.append(f"     {path}")
        if scope or nm_type:
            lines.append(f"     scope={scope}  type={nm_type}")
    return "\n".join(lines)


def format_full(notes: list[dict[str, Any]]) -> str:
    sections: list[str] = []
    for i, n in enumerate(notes, 1):
        title = n.get("title", n.get("_stem", "untitled"))
        path = n.get("_path", "")
        abs_path = n.get("_abs_path", "")
        tier = n.get("retrieval_tier", "?")
        scope = n.get("scope", "")
        nm_type = n.get("type", "")
        tags = n.get("tags", [])

        header = f"### {i}. {title}\n"
        meta_line = f"**path**: `{path}`\n"
        meta_line += f"**tier**: {tier} | **type**: {nm_type} | **scope**: {scope}\n"
        if tags:
            meta_line += f"**tags**: {', '.join(tags)}\n"

        body = ""
        if abs_path and os.path.isfile(abs_path):
            try:
                content = Path(abs_path).read_text(encoding="utf-8", errors="replace")
                preview = extract_body_preview(content, max_lines=10)
                if preview:
                    body = f"\n```\n{preview}\n```\n"
            except OSError:
                pass

        sections.append(header + meta_line + body)
    return "\n---\n".join(sections)


def format_json(notes: list[dict[str, Any]]) -> str:
    clean = [{k: v for k, v in n.items() if not k.startswith("_abs")} for n in notes]
    return json.dumps(clean, ensure_ascii=False, indent=2)


def print_stats(notes: list[dict[str, Any]]) -> str:
    total = len(notes)
    by_type: dict[str, int] = {}
    by_scope: dict[str, int] = {}
    by_tier: dict[str, int] = {}

    for n in notes:
        by_type[n.get("type", "unknown")] = by_type.get(n.get("type", "unknown"), 0) + 1
        s = n.get("scope") or ""
        if isinstance(s, list):
            for v in s:
                by_scope[str(v)] = by_scope.get(str(v), 0) + 1
        elif s:
            by_scope[str(s)] = by_scope.get(str(s), 0) + 1
        tier = n.get("retrieval_tier", "?")
        by_tier[tier] = by_tier.get(tier, 0) + 1

    lines = [
        "=== bongsu.search Stats ===",
        f"Total indexed notes: {total}",
        "",
        "--- By Retrieval Tier ---",
    ]
    for k in sorted(by_tier, reverse=True):
        lines.append(f"  {k}: {by_tier[k]}")
    lines.append("\n--- Top 15 Scopes ---")
    for k, v in sorted(by_scope.items(), key=lambda x: -x[1])[:15]:
        lines.append(f"  {k}: {v}")
    lines.append("\n--- Top 15 Types ---")
    for k, v in sorted(by_type.items(), key=lambda x: -x[1])[:15]:
        lines.append(f"  {k}: {v}")
    return "\n".join(lines)


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Search a vault by frontmatter and/or body text."
    )
    parser.add_argument("--vault", "--vault-root", type=Path, required=True,
                        help="vault root directory")
    parser.add_argument("--scope", help="filter by scope (canonicalized via .sillok/scope-aliases.yaml)")
    parser.add_argument("--type", dest="note_type",
                        help="filter by note type (e.g. pattern, decision, case)")
    parser.add_argument("--tier", help="filter by retrieval tier (A/B/C)")
    parser.add_argument("--status", help="filter by status (active/draft/archived)")
    parser.add_argument("--topic", help="filter by topic/subtopic")
    parser.add_argument("--date-from", help="filter notes from date (YYYY-MM-DD)")
    parser.add_argument("--query", "-q", help="full-text body search (rg -> grep)")
    parser.add_argument("--format", "-f",
                        choices=["summary", "full", "json"], default="summary")
    parser.add_argument("--limit", "-n", type=int, default=20,
                        help="max results (default 20)")
    parser.add_argument("--stats", action="store_true", help="show index statistics")
    parser.add_argument("--search-dir", action="append", default=[],
                        help="restrict to a vault sub-directory (repeatable)")
    args = parser.parse_args(argv)

    vault_root: Path = args.vault.resolve()
    if not vault_root.exists():
        print(f"Error: vault root not found: {vault_root}", file=sys.stderr)
        return 1

    search_dirs = tuple(args.search_dir) if args.search_dir else DEFAULT_SEARCH_DIRS
    alias_map = load_scope_aliases(vault_root)

    t0 = time.time()
    notes = build_index(vault_root, search_dirs)
    index_time = time.time() - t0

    if args.stats:
        print(print_stats(notes))
        print(f"\nIndex time: {index_time:.2f}s")
        return 0

    filtered = filter_notes(
        notes,
        scope=args.scope,
        note_type=args.note_type,
        tier=args.tier,
        status=args.status,
        topic=args.topic,
        date_from=args.date_from,
        alias_map=alias_map,
    )

    if args.query:
        matching_paths = fulltext_search(vault_root, search_dirs, args.query)
        if filtered:
            filtered = [n for n in filtered if n.get("_path") in matching_paths]
        else:
            filtered = [n for n in notes if n.get("_path") in matching_paths]

    tier_order = {"A": 0, "B": 1, "C": 2}
    filtered.sort(key=lambda n: (
        tier_order.get(str(n.get("retrieval_tier", "C")), 3),
        -float(n.get("quality_score", 0) or 0),
    ))

    total_matched = len(filtered)
    filtered = filtered[: args.limit]
    search_time = time.time() - t0

    if args.format == "json":
        print(format_json(filtered))
    elif args.format == "full":
        print(format_full(filtered))
    else:
        print(format_summary(filtered))

    print(f"\n--- {total_matched} matched / {len(notes)} indexed / {search_time:.2f}s ---")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
