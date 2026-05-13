"""sillok.eval.triangulation — Bond Evidence Principles #3 (triangulation gate).

Heuristically extracts candidate claims from a markdown report and counts
nearby source citations (markdown links, ``Source:``-style annotations,
footnote refs). Claims that fall short of ``min_sources`` are surfaced as
gate failures.

This is a *lightweight* port of the upstream ``bond-triangulation-check.py``
script. It is intentionally heuristic, not parser-grade — the goal is to
catch obvious triangulation gaps in CI without forcing every report into a
rigid format. Reports written for high-evidence audiences (board / regulator)
should use the full upstream tool.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable


CLAIM_BULLET_RE = re.compile(r"^\s*[-*+]\s+(.+)$")
CLAIM_NUMBERED_RE = re.compile(r"^\s*\d+\.\s+(.+)$")
LINK_RE = re.compile(r"\[[^\]]+\]\([^)]+\)")
SOURCE_INLINE_RE = re.compile(r"(?:Source|Src|출처|참고|reference)\s*[:：]", re.IGNORECASE)
FOOTNOTE_REF_RE = re.compile(r"\[\^[^\]]+\]")
SECTION_RE = re.compile(
    r"^##\s+(Executive Summary|Key Findings|Findings|Highlights|Top Insights|개요|핵심 요약)",
    re.IGNORECASE,
)


@dataclass
class FailingClaim:
    line: int
    text: str
    source_count: int


@dataclass
class TriangulationResult:
    total: int
    passed: int
    failures: list[FailingClaim] = field(default_factory=list)
    min_sources_required: int = 3

    @property
    def pass_rate_pct(self) -> float:
        return 100.0 * self.passed / self.total if self.total else 0.0


def _section_lines(text: str) -> Iterable[tuple[int, str]]:
    """Yield (line_no, line) tuples within sections that should carry claims."""
    lines = text.splitlines()
    in_target = False
    for i, line in enumerate(lines, start=1):
        if line.startswith("## "):
            in_target = bool(SECTION_RE.match(line))
            continue
        if line.startswith("# "):
            in_target = False
            continue
        if in_target:
            yield i, line


def _count_sources_near(line_no: int, lines: list[str], radius: int = 5) -> int:
    """Count source-y signals within ±radius lines of the given line."""
    lo = max(0, line_no - 1 - radius)
    hi = min(len(lines), line_no + radius)
    window = "\n".join(lines[lo:hi])
    return (
        len(LINK_RE.findall(window))
        + len(FOOTNOTE_REF_RE.findall(window))
        + len(SOURCE_INLINE_RE.findall(window))
    )


def check_triangulation(text: str, min_sources: int = 3) -> TriangulationResult:
    """Score a markdown report against Bond #3 (≥``min_sources`` per claim)."""
    lines = text.splitlines()
    claims: list[tuple[int, str]] = []
    for line_no, line in _section_lines(text):
        match = CLAIM_BULLET_RE.match(line) or CLAIM_NUMBERED_RE.match(line)
        if match:
            claims.append((line_no, match.group(1).strip()))

    failures: list[FailingClaim] = []
    passed = 0
    for line_no, claim in claims:
        count = _count_sources_near(line_no, lines)
        if count >= min_sources:
            passed += 1
        else:
            failures.append(FailingClaim(line=line_no, text=claim, source_count=count))

    return TriangulationResult(
        total=len(claims),
        passed=passed,
        failures=failures,
        min_sources_required=min_sources,
    )
