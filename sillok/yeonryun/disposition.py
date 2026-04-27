"""yeonryun.disposition — automated knowledge disposition engine.

Sanitized port of the upstream ``vault-disposition.py``. Scores a research
or result markdown file for *reusability* and decides whether the content
should:

  - ``none``               — stay where it is (single-use, ephemeral)
  - ``local-reusable``     — be absorbed into the local repo's handbook
                             or templates folder
  - ``cross-repo-reusable``— be promoted to the shared vault as one or
                             more atomic notes

This is the **promotion** half of the auto-growth loop (see Sillok README
§Yeonryun). The retrieval half lives in :mod:`sillok.bongsu`.

CLI::

    python -m sillok.yeonryun.disposition path/to/notes.md
    python -m sillok.yeonryun.disposition --scan research/ --auto-extract \\
        --vault ~/Documents/my-vault \\
        --target-dir 40_Knowledge/auto

Public API:

  - :func:`score_reusability`        — content-only scorer
  - :func:`determine_disposition`    — disposition + extractable atoms
  - :func:`identify_extractable_atoms`
  - :func:`generate_atomic_note`
  - :func:`process_file`
  - :func:`scan_directory`
  - :func:`format_report`
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)


# ----------------------------------------------------------------------
# Reusability signals
# ----------------------------------------------------------------------

# (regex, atom-type, weight). Bilingual (en/ko) by default; downstream
# users can subclass / monkeypatch this list to add domain-specific
# signals without forking the module.
REUSABLE_PATTERNS: list[tuple[str, str, int]] = [
    (r"(?:pattern|패턴|principle|원칙|rule|규칙)", "pattern", 3),
    (r"(?:checklist|체크리스트|점검|검증)", "checklist", 3),
    (r"(?:prompt|프롬프트|command|명령어)", "prompt", 2),
    (r"(?:decision|의사결정|criteria|판단 기준)", "decision", 3),
    (r"(?:template|템플릿|양식|form)", "template", 2),
    (r"(?:case|사례|example|케이스|실사례)", "case", 2),
    (r"(?:comparison|비교|analysis|분석|insight)", "insight", 2),
    (r"(?:workflow|워크플로|pipeline|파이프라인|process|프로세스)", "pattern", 2),
    (r"(?:best.?practice|모범|권장)", "pattern", 3),
    (r"(?:lesson|교훈|learning|학습|배운)", "decision", 2),
]

EPHEMERAL_PATTERNS: list[str] = [
    r"(?:debug|디버그|hotfix|긴급)",
    r"(?:one-time|일회성|temporary|임시)",
    r"(?:workaround|우회|bypass)",
]

MIN_CONTENT_LENGTH = 500
CROSS_REPO_THRESHOLD = 6
LOCAL_THRESHOLD = 3

# Atom-type priority for representative atom selection. When multiple
# atom types are extractable from the same source, only the highest
# priority is materialized by default — full materialization
# (``--extract-all``) is opt-in to avoid signal/noise degradation in
# the receiving vault.
_ATOM_TYPE_PRIORITY: dict[str, int] = {
    "pattern": 6,
    "decision": 5,
    "checklist": 4,
    "template": 3,
    "case": 2,
    "prompt": 1,
    "insight": 0,
}


# ----------------------------------------------------------------------
# Frontmatter helpers
# ----------------------------------------------------------------------


def parse_frontmatter(content: str) -> dict[str, str]:
    m = FRONTMATTER_RE.match(content)
    if not m:
        return {}
    meta: dict[str, str] = {}
    for line in m.group(1).splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, _, value = line.partition(":")
        meta[key.strip()] = value.strip().strip("\"'")
    return meta


def extract_body(content: str) -> str:
    return FRONTMATTER_RE.sub("", content, count=1).strip()


# ----------------------------------------------------------------------
# Scoring
# ----------------------------------------------------------------------


def score_reusability(content: str) -> tuple[int, list[dict[str, Any]]]:
    """Score ``content`` for reusability. Returns ``(score, signals)``.

    Higher score = more likely a reusable knowledge atom. The score is
    clamped at ``>= 0``; ephemeral patterns subtract from it but cannot
    drive it negative.
    """
    body_lower = content.lower()
    score = 0
    signals: list[dict[str, Any]] = []

    for pattern, knowledge_type, weight in REUSABLE_PATTERNS:
        matches = re.findall(pattern, body_lower, re.IGNORECASE)
        if matches:
            score += weight * min(len(matches), 3)
            signals.append({
                "type": knowledge_type,
                "pattern": pattern,
                "count": len(matches),
                "weight": weight,
            })

    for pattern in EPHEMERAL_PATTERNS:
        if re.search(pattern, body_lower, re.IGNORECASE):
            score -= 3
            signals.append({"type": "ephemeral", "pattern": pattern, "weight": -3})

    headers = len(re.findall(r"^#{1,4}\s", content, re.MULTILINE))
    tables = len(re.findall(r"^\|", content, re.MULTILINE))
    code_blocks = len(re.findall(r"```", content))
    if headers >= 5:
        score += 2
    if tables >= 3:
        score += 2
    if code_blocks >= 2:
        score += 1

    if len(content) > 3000:
        score += 1
    if len(content) > 10000:
        score += 2

    return max(score, 0), signals


def determine_disposition(content: str, meta: dict[str, Any] | None = None) -> dict[str, Any]:
    """Decide a disposition level for the document.

    Returns a dict with ``disposition``, ``reason``, ``score``,
    ``signals``, and ``extractable_atoms``.
    """
    body = extract_body(content)

    if len(body) < MIN_CONTENT_LENGTH:
        return {
            "disposition": "none",
            "reason": f"content too short ({len(body)} chars < {MIN_CONTENT_LENGTH})",
            "score": 0,
            "signals": [],
            "extractable_atoms": [],
        }

    meta = meta or {}
    score, signals = score_reusability(content)

    if score >= CROSS_REPO_THRESHOLD:
        disposition = "cross-repo-reusable"
    elif score >= LOCAL_THRESHOLD:
        disposition = "local-reusable"
    else:
        disposition = "none"

    atoms = identify_extractable_atoms(content, signals, meta)

    result: dict[str, Any] = {
        "disposition": disposition,
        "reason": f"reusability score {score} (cross-repo>={CROSS_REPO_THRESHOLD}, local>={LOCAL_THRESHOLD})",
        "score": score,
        "signals": signals,
        "extractable_atoms": atoms,
    }
    # Carry source-frontmatter signals through for callers that want to
    # honor an existing retrieval_tier / quality_score without having to
    # re-parse the file.
    for key in ("retrieval_tier", "quality_score"):
        if key in meta:
            result[f"source_{key}"] = meta[key]
    return result


# ----------------------------------------------------------------------
# Atom extraction
# ----------------------------------------------------------------------


def identify_extractable_atoms(
    content: str,
    signals: list[dict[str, Any]],
    meta: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Identify sections that could become atomic vault notes.

    Honors two frontmatter opt-out keys when present in ``meta``:

      - ``cross_repo: false`` — author has marked the document as
        repo-local, do not extract anything.
      - ``disposition: none`` — same effect, equivalent spelling.
    """
    meta = meta or {}
    if str(meta.get("cross_repo", "")).lower() == "false":
        return []
    if str(meta.get("disposition", "")).lower() == "none":
        return []

    atoms: list[dict[str, Any]] = []
    seen_types: set[str] = set()

    for sig in signals:
        kt = sig.get("type", "")
        if kt in seen_types or kt == "ephemeral":
            continue
        seen_types.add(kt)
        atoms.append({
            "knowledge_type": kt,
            "source_section": _find_section_for_type(content, kt),
            "reusability": "high" if sig.get("weight", 0) >= 3 else "medium",
        })

    return atoms[:5]


def _find_section_for_type(content: str, knowledge_type: str) -> str:
    type_patterns = {
        "pattern": r"(?:pattern|패턴|workflow|워크플로|process|프로세스|best.?practice)",
        "checklist": r"(?:checklist|체크리스트|점검|검증)",
        "prompt": r"(?:prompt|프롬프트|command|명령)",
        "decision": r"(?:decision|의사결정|판단|lesson|교훈)",
        "template": r"(?:template|템플릿|양식)",
        "case": r"(?:case|사례|example|예시)",
        "insight": r"(?:comparison|비교|analysis|분석|insight|인사이트|conclusion|결론|summary|요약)",
    }
    pattern = type_patterns.get(knowledge_type, "")
    if not pattern:
        return ""
    for line in content.splitlines():
        if line.startswith("#") and re.search(pattern, line, re.IGNORECASE):
            return line.strip().lstrip("#").strip()
    return ""


def _extract_section_content(content: str, section_title: str) -> str:
    if not section_title:
        return ""
    lines = content.splitlines()
    capturing = False
    captured: list[str] = []
    target_level = 0

    for line in lines:
        if not capturing:
            if section_title.lower() in line.lower() and line.startswith("#"):
                capturing = True
                target_level = len(line) - len(line.lstrip("#"))
                continue
        else:
            if line.startswith("#"):
                level = len(line) - len(line.lstrip("#"))
                if level <= target_level:
                    break
            captured.append(line)

    return "\n".join(captured).strip()[:1500]


def _pick_representative_atom(atoms: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not atoms:
        return None
    return max(
        atoms,
        key=lambda a: (
            _ATOM_TYPE_PRIORITY.get(a.get("knowledge_type", ""), 0),
            1 if a.get("reusability") == "high" else 0,
        ),
    )


# ----------------------------------------------------------------------
# Atomic note generation
# ----------------------------------------------------------------------


def generate_atomic_note(
    atom: dict[str, Any],
    source_path: str,
    source_meta: dict[str, Any],
    content: str,
    *,
    source_repo: str | None = None,
    topic: str = "general",
) -> str:
    """Generate a vault-compatible atomic note from an extractable atom.

    ``source_repo`` defaults to the ``SILLOK_SOURCE_REPO`` env var, then
    to ``"sillok"``. Set it explicitly when you want the note's
    provenance to point at a specific GitHub coordinate.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    kt = atom["knowledge_type"]
    section = atom.get("source_section", "")

    section_content = _extract_section_content(content, section) if section else ""
    if not section_content:
        section_content = extract_body(content)[:2000]

    repo = source_repo or os.environ.get("SILLOK_SOURCE_REPO", "sillok")
    # Honor a topic value carried in the source's own frontmatter when the
    # caller hasn't passed an explicit override.
    if topic == "general" and source_meta.get("topic"):
        topic = str(source_meta["topic"])
    title = f"[Auto] {section or kt} — from {Path(source_path).stem}"

    note = f"""---
title: "{title}"
type: atomic/insight
status: draft
topic: {topic}
subtopic: "{kt}"
tags: [auto-extracted]
source-system: sillok.yeonryun
source_repo: {repo}
source_result: "{source_path}"
extraction_date: '{today}'
retrieval_tier: B
quality_score: 0.6
---

## Core Message

> {kt} — auto-extracted reusable knowledge atom

## Key Content

{section_content[:1500]}

## Reuse Conditions

- **knowledge_type**: {kt}
- **reusability**: {atom.get('reusability', 'medium')}
- **source**: `{source_path}`
- **auto-extracted**: {today}

## Related Concepts

- Extracted from source. Manual review and link curation required.
"""
    return note


# ----------------------------------------------------------------------
# File operations
# ----------------------------------------------------------------------


def process_file(
    filepath: str | os.PathLike[str],
    *,
    auto_extract: bool = False,
    extract_all: bool = False,
    target_dir: Path | None = None,
    vault_root: Path | None = None,
    source_repo: str | None = None,
    topic: str = "general",
) -> dict[str, Any]:
    """Process a single ``.md`` file and return a disposition result.

    Parameters
    ----------
    filepath:
        Path to the source markdown file.
    auto_extract:
        When true, materialize atomic vault notes for the file.
    extract_all:
        When true, generate one atomic note per detected atom type.
        Default (false) generates only the highest-priority atom — this
        avoids signal/noise degradation in the receiving vault.
    target_dir:
        Directory to write atomic notes into. Required when
        ``auto_extract`` is true; ignored otherwise.
    vault_root:
        When set, ``extracted_files`` paths are reported relative to it
        (otherwise absolute paths are used).
    source_repo:
        Provenance string written into the atomic note frontmatter.
    topic:
        ``topic`` value written into the atomic note frontmatter.
    """
    path = Path(filepath)
    if not path.exists() or path.suffix != ".md":
        return {"file": str(path), "error": "file not found or not a .md file"}

    content = path.read_text(encoding="utf-8", errors="replace")
    meta = parse_frontmatter(content)
    result = determine_disposition(content, meta)
    result["file"] = str(path)
    result["title"] = meta.get("title", path.stem)

    if auto_extract and result["extractable_atoms"]:
        if str(path).startswith("/tmp/"):
            result["warning"] = (
                "/tmp/ paths are not auto-extract targets "
                "(canonical source_path cannot be guaranteed)"
            )
        elif target_dir is None:
            result["warning"] = (
                "auto_extract=True requires target_dir — skipping materialization"
            )
        else:
            result["extracted_files"] = []
            atoms = result["extractable_atoms"]
            if not extract_all:
                rep = _pick_representative_atom(atoms)
                atoms = [rep] if rep else []
            for atom in atoms:
                note_content = generate_atomic_note(
                    atom, str(path), meta, content,
                    source_repo=source_repo, topic=topic,
                )
                slug = re.sub(r"[^a-z0-9]+", "-", atom["knowledge_type"].lower())
                stem = path.stem[:40]
                filename = f"auto-{slug}-{stem}.md"
                target = target_dir / filename

                if not target.exists():
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text(note_content, encoding="utf-8")
                    if vault_root is not None:
                        try:
                            result["extracted_files"].append(
                                str(target.relative_to(vault_root))
                            )
                            continue
                        except ValueError:
                            pass
                    result["extracted_files"].append(str(target))

    return result


def scan_directory(
    dirpath: str | os.PathLike[str],
    *,
    auto_extract: bool = False,
    extract_all: bool = False,
    target_dir: Path | None = None,
    vault_root: Path | None = None,
    source_repo: str | None = None,
    topic: str = "general",
) -> list[dict[str, Any]]:
    """Recursively scan ``dirpath`` for ``.md`` files."""
    results: list[dict[str, Any]] = []
    for md_file in sorted(Path(dirpath).rglob("*.md")):
        result = process_file(
            md_file,
            auto_extract=auto_extract,
            extract_all=extract_all,
            target_dir=target_dir,
            vault_root=vault_root,
            source_repo=source_repo,
            topic=topic,
        )
        results.append(result)
    return results


# ----------------------------------------------------------------------
# Output formatting
# ----------------------------------------------------------------------


def format_report(results: list[dict[str, Any]]) -> str:
    lines: list[str] = ["# Vault Disposition Report", ""]
    lines.append(f"**date**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"**files scanned**: {len(results)}")
    lines.append("")

    by_disp: dict[str, list[dict[str, Any]]] = {
        "none": [], "local-reusable": [], "cross-repo-reusable": [],
    }
    for r in results:
        d = r.get("disposition", "none")
        by_disp.setdefault(d, []).append(r)

    lines.append("## Summary")
    lines.append(f"- cross-repo-reusable: {len(by_disp.get('cross-repo-reusable', []))}")
    lines.append(f"- local-reusable: {len(by_disp.get('local-reusable', []))}")
    lines.append(f"- none: {len(by_disp.get('none', []))}")
    lines.append("")

    for level in ("cross-repo-reusable", "local-reusable", "none"):
        items = by_disp.get(level, [])
        if not items:
            continue
        lines.append(f"## {level} ({len(items)})")
        for r in items:
            title = r.get("title", r.get("file", "unknown"))
            score = r.get("score", 0)
            reason = r.get("reason", "")
            lines.append(f"- **{title}** (score={score}) — {reason}")
            for ef in r.get("extracted_files", []) or []:
                lines.append(f"  - extracted: `{ef}`")
        lines.append("")

    return "\n".join(lines)


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Score markdown content for reusability and decide its disposition.",
    )
    parser.add_argument("file", nargs="?", help="single .md file to analyze")
    parser.add_argument("--scan", help="scan a directory recursively for .md files")
    parser.add_argument("--auto-extract", action="store_true",
                        help="materialize atomic vault notes for reusable content "
                             "(requires --target-dir)")
    parser.add_argument("--extract-all", action="store_true",
                        help="generate one atomic note per atom type (default: only "
                             "the highest-priority representative atom — opt-in to "
                             "avoid signal/noise degradation)")
    parser.add_argument("--vault", "--vault-root", type=Path, default=None,
                        help="vault root directory (used to render relative paths "
                             "in --auto-extract output)")
    parser.add_argument("--target-dir", type=Path, default=None,
                        help="directory to write atomic notes into "
                             "(required for --auto-extract)")
    parser.add_argument("--source-repo", default=None,
                        help="provenance string written into the atomic note frontmatter "
                             "(default: $SILLOK_SOURCE_REPO env var or 'sillok')")
    parser.add_argument("--topic", default="general",
                        help="topic value for atomic note frontmatter (default: 'general')")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args(argv)

    if not args.file and not args.scan:
        parser.print_help()
        return 1

    if args.auto_extract and args.target_dir is None:
        print("Error: --auto-extract requires --target-dir", file=sys.stderr)
        return 2

    common = dict(
        auto_extract=args.auto_extract,
        extract_all=args.extract_all,
        target_dir=args.target_dir,
        vault_root=args.vault,
        source_repo=args.source_repo,
        topic=args.topic,
    )

    if args.scan:
        results = scan_directory(args.scan, **common)
    else:
        results = [process_file(args.file, **common)]

    if args.format == "json":
        for r in results:
            for s in r.get("signals", []):
                s.pop("pattern", None)
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print(format_report(results))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
