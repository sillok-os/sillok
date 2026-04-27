"""Shared frontmatter parsing helpers for sillok.bongsu.

Sanitized port of the upstream `vault_common.py`. The original module
held client-canonicalization tables (mapping 'samsung' / 'lg' / 'kt' /
etc. to internal slugs). That logic stays internal to the maintainer's
vault and is replaced here with a generic, opt-in alias map loaded from
``.sillok/scope-aliases.yaml`` if present.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)


def _scalar(fm_text: str, key: str) -> str:
    match = re.search(rf"^{re.escape(key)}:\s*(.+)$", fm_text, re.MULTILINE)
    return match.group(1).strip().strip("\"'") if match else ""


def _parse_fm_list(fm_text: str, key: str) -> list[str]:
    inline = re.search(rf"^{re.escape(key)}:\s*(\[.*?\])\s*$", fm_text, re.MULTILINE)
    if inline:
        raw = inline.group(1).strip()
        if raw == "[]":
            return []
        quoted = [
            next(part for part in match if part)
            for match in re.findall(r'"([^"]+)"|\'([^\']+)\'', raw)
        ]
        if quoted:
            return quoted
        return [item.strip() for item in raw.strip("[]").split(",") if item.strip()]
    multi = re.search(
        rf"^{re.escape(key)}:\s*\n((?:[ \t]+-[ \t]+.+\n?)+)", fm_text, re.MULTILINE
    )
    if multi:
        return [
            re.sub(r"^[ \t]+-[ \t]+", "", line).strip().strip("\"'")
            for line in multi.group(1).splitlines()
            if line.strip()
        ]
    return []


# Default frontmatter keys that get pulled into the index. Configurable via
# `.sillok/config.toml` [bongsu.search] indexed_scalar_keys / indexed_list_keys.
DEFAULT_SCALAR_KEYS = (
    "title", "type", "status", "topic", "subtopic",
    "scope", "category", "industry", "domain",
    "retrieval_tier", "quality_score", "token_count",
    "extraction_date", "session_date_iso", "date",
    "source-system", "program",
)

DEFAULT_LIST_KEYS = ("tags", "related")


def parse_frontmatter(
    content: str,
    scalar_keys: tuple[str, ...] = DEFAULT_SCALAR_KEYS,
    list_keys: tuple[str, ...] = DEFAULT_LIST_KEYS,
) -> dict[str, Any]:
    """Extract YAML frontmatter as dict. Returns ``{}`` if no frontmatter.

    Reads only the keys named in ``scalar_keys`` / ``list_keys``. Unknown
    keys are silently ignored — pass an explicit list to include extras.
    """
    m = FRONTMATTER_RE.match(content)
    if not m:
        return {}
    fm_text = m.group(1)
    meta: dict[str, Any] = {}
    for key in scalar_keys:
        val = _scalar(fm_text, key)
        if val:
            meta[key] = val
    for key in list_keys:
        vals = _parse_fm_list(fm_text, key)
        if vals:
            meta[key] = vals
    return meta


def extract_body_preview(content: str, max_lines: int = 15) -> str:
    """Extract body text after frontmatter (truncated to ``max_lines``)."""
    body = FRONTMATTER_RE.sub("", content, count=1).strip()
    lines = body.splitlines()
    if len(lines) > max_lines:
        lines = lines[:max_lines]
    return "\n".join(lines)


def match_field(note: dict[str, Any], key: str, value: str) -> bool:
    """Case-insensitive partial match between a note's field and a value."""
    note_val = note.get(key, "")
    if isinstance(note_val, list):
        return any(value.lower() in v.lower() for v in note_val)
    return value.lower() in str(note_val).lower()


def load_scope_aliases(vault_root: Path) -> dict[str, str]:
    """Load an opt-in alias map from ``<vault>/.sillok/scope-aliases.yaml``.

    Returns ``{}`` if the file does not exist or PyYAML is not installed.
    Format::

        aliases:
          acme:        ["acme-corp", "acme-inc"]
          globex:      ["globex-systems"]
    """
    path = vault_root / ".sillok" / "scope-aliases.yaml"
    if not path.exists():
        return {}
    try:
        import yaml  # type: ignore

        payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}
    aliases = payload.get("aliases", {}) or {}
    flat: dict[str, str] = {}
    for canonical, alts in aliases.items():
        flat[canonical.lower()] = canonical
        for alt in alts or []:
            flat[str(alt).lower()] = canonical
    return flat


def canonicalize_scope(value: str | None, alias_map: dict[str, str]) -> str:
    """Map a raw frontmatter scope value to its canonical form."""
    if not value:
        return ""
    return alias_map.get(value.lower(), value)


def note_matches_scope(note: dict[str, Any], scope: str, alias_map: dict[str, str]) -> bool:
    """Match a note's ``scope`` field (or list of scopes) against a target."""
    raw = note.get("scope") or ""
    target = scope.lower()
    if isinstance(raw, list):
        for v in raw:
            if canonicalize_scope(str(v), alias_map).lower() == target:
                return True
        return False
    return canonicalize_scope(str(raw), alias_map).lower() == target


__all__ = [
    "FRONTMATTER_RE",
    "DEFAULT_SCALAR_KEYS",
    "DEFAULT_LIST_KEYS",
    "parse_frontmatter",
    "extract_body_preview",
    "match_field",
    "load_scope_aliases",
    "canonicalize_scope",
    "note_matches_scope",
]
