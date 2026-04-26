"""Markdown ingest — Phase 0 bootstrap of Top 10 Feature #1.

Walks a vault directory, parses frontmatter + body of every ``.md`` file,
and writes a JSONL index to ``<vault>/.sillok-janggyeong/index.jsonl``.

Vault-resident only (per ADR 0001 / D3): the index lives **inside** the
vault directory so that any backup or sync mechanism that already covers
the vault (git, iCloud, Dropbox, OneDrive) covers the corpus too.

PR-K (Phase 2) extends this to pdf / docx / xlsx / pptx / txt / hwpx.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

INDEX_DIRNAME = ".sillok-janggyeong"
INDEX_FILENAME = "index.jsonl"
DEFAULT_EXCLUDES = (".git", ".obsidian", ".sillok", ".sillok-janggyeong",
                    "node_modules", "__pycache__", ".venv")


@dataclass
class Atom:
    """Lightweight in-memory representation of an indexed file."""

    path: str
    sha256: str
    mtime: float
    size: int
    frontmatter: dict[str, Any] = field(default_factory=dict)
    body_preview: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Parse YAML frontmatter at the head of an md file. Returns (fm, body).

    The parser is intentionally minimal: it accepts a leading ``---`` block
    delimited by another ``---`` line and tries ``yaml.safe_load`` if PyYAML
    is available. Without PyYAML, the frontmatter dict is empty (the body
    is still indexed).
    """
    if not text.startswith("---"):
        return {}, text
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text
    closing = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            closing = i
            break
    if closing < 0:
        return {}, text
    fm_text = "\n".join(lines[1:closing])
    body = "\n".join(lines[closing + 1 :])
    fm: dict[str, Any] = {}
    try:
        import yaml  # type: ignore

        loaded = yaml.safe_load(fm_text)
        if isinstance(loaded, dict):
            fm = loaded
    except Exception:
        fm = {}
    return fm, body


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def _is_excluded(path: Path, vault: Path, excludes: tuple[str, ...]) -> bool:
    rel = path.relative_to(vault)
    for part in rel.parts:
        if part in excludes:
            return True
    return False


def ingest_md(
    vault: Path,
    *,
    excludes: tuple[str, ...] = DEFAULT_EXCLUDES,
    body_preview_chars: int = 500,
) -> int:
    """Walk ``vault`` and (re)write the index. Returns number of files indexed.

    The index is rewritten atomically (temp + rename). Any file that is
    unreadable or has a non-utf8 payload is skipped with a stderr warning;
    the rest of the vault is still indexed.
    """
    vault = vault.resolve()
    if not vault.is_dir():
        raise NotADirectoryError(f"vault not found: {vault}")

    index_dir = vault / INDEX_DIRNAME
    index_dir.mkdir(parents=True, exist_ok=True)
    index_path = index_dir / INDEX_FILENAME
    tmp_path = index_path.with_suffix(".jsonl.tmp")

    count = 0
    with tmp_path.open("w", encoding="utf-8") as out:
        for root, dirs, files in os.walk(vault):
            root_path = Path(root)
            # prune excluded dirs in-place
            dirs[:] = [d for d in dirs if d not in excludes]
            for name in files:
                if not name.endswith(".md"):
                    continue
                fp = root_path / name
                try:
                    if _is_excluded(fp, vault, excludes):
                        continue
                    raw = fp.read_text(encoding="utf-8")
                except (OSError, UnicodeDecodeError) as exc:
                    print(f"skip {fp}: {exc}", file=sys.stderr)
                    continue
                fm, body = _parse_frontmatter(raw)
                stat = fp.stat()
                atom = Atom(
                    path=str(fp.relative_to(vault)),
                    sha256=_hash_text(raw),
                    mtime=stat.st_mtime,
                    size=stat.st_size,
                    frontmatter=fm,
                    body_preview=body[:body_preview_chars],
                )
                out.write(json.dumps(atom.to_dict(), ensure_ascii=False) + "\n")
                count += 1

    os.replace(tmp_path, index_path)
    return count


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "vault",
        type=Path,
        help="path to the vault root (e.g. ~/Documents/my-vault)",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="additional directory names to exclude (repeatable)",
    )
    parser.add_argument(
        "--preview-chars",
        type=int,
        default=500,
        help="how many leading characters of body to keep in the index",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    excludes = tuple(list(DEFAULT_EXCLUDES) + list(args.exclude))
    n = ingest_md(args.vault, excludes=excludes, body_preview_chars=args.preview_chars)
    if args.json:
        print(json.dumps({"indexed": n, "vault": str(args.vault.resolve())}))
    else:
        print(f"indexed {n} markdown file(s) under {args.vault.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
