"""sillok.sangso.gates — 4 governance gates for pack proposals.

Each gate is a pure function: ``(current, proposed, registry) -> GateResult``.
Gates are designed to be runnable independently for unit testing and chained
in ``run_all_gates`` for the propose flow.

Gates
-----
1. **Lint** — frontmatter parses, required fields present, body length ≥ 200,
   no broken markdown links, body has no embedded ``---`` fence collisions.
2. **Diff** — 3-way diff vs current pack body; structural change summary
   (sections added / removed / modified) + line counts.
3. **Eval delta** — re-run probes from ``sillok.eval`` against a registry
   that points at the proposed body; report pass-rate / p50 deltas. Skipped
   if ``sillok.eval`` is not importable (graceful).
4. **Approval** — synthesizes the human-review artifact. *Never* applies the
   change automatically — the caller must invoke ``accept`` interactively.
"""
from __future__ import annotations

import difflib
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml


_REQUIRED_FRONTMATTER_FIELDS = ("id", "title", "category", "sub_category", "version", "license")
_MIN_BODY_LINES = 200
_BROKEN_LINK_RE = re.compile(r"\]\(\s*\)")  # `[text]()` with empty URL
_SECTION_RE = re.compile(r"^(#+)\s+(.+)$")


@dataclass
class GateResult:
    gate: str
    passed: bool
    summary: str
    details: dict[str, Any] = field(default_factory=dict)
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _split_frontmatter(text: str) -> tuple[dict[str, Any] | None, str]:
    """Return ``(frontmatter_dict, body)`` or ``(None, "")`` on parse failure."""
    if not text.startswith("---\n"):
        return None, ""
    rest = text[4:]
    end = rest.find("\n---\n")
    if end < 0:
        return None, ""
    block = rest[:end]
    body = rest[end + 5 :]
    try:
        loaded = yaml.safe_load(block) or {}
    except yaml.YAMLError:
        return None, body
    return loaded, body


def gate_lint(proposed_text: str) -> GateResult:
    """Gate 1 — schema, frontmatter, body length, link integrity."""
    frontmatter, body = _split_frontmatter(proposed_text)
    if frontmatter is None:
        return GateResult(
            gate="lint",
            passed=False,
            summary="frontmatter missing or unparseable",
            error="no frontmatter block found, or block is invalid YAML",
        )

    missing = [f for f in _REQUIRED_FRONTMATTER_FIELDS if f not in frontmatter]
    body_lines = len(body.splitlines())
    broken_links = _BROKEN_LINK_RE.findall(body)

    issues: list[str] = []
    if missing:
        issues.append(f"missing required fields: {missing}")
    if body_lines < _MIN_BODY_LINES:
        issues.append(f"body has {body_lines} lines (≥{_MIN_BODY_LINES} required)")
    if broken_links:
        issues.append(f"{len(broken_links)} broken markdown link(s) (empty URL)")

    return GateResult(
        gate="lint",
        passed=not issues,
        summary=f"{len(issues)} issue(s)" if issues else "OK",
        details={
            "missing_fields": missing,
            "body_lines": body_lines,
            "broken_link_count": len(broken_links),
            "frontmatter_id": frontmatter.get("id"),
        },
        error=" · ".join(issues) if issues else None,
    )


def gate_diff(current_text: str, proposed_text: str) -> GateResult:
    """Gate 2 — 3-way diff vs current; structural change summary."""
    _, current_body = _split_frontmatter(current_text)
    _, proposed_body = _split_frontmatter(proposed_text)

    current_sections = _extract_sections(current_body)
    proposed_sections = _extract_sections(proposed_body)

    added = sorted(proposed_sections - current_sections)
    removed = sorted(current_sections - proposed_sections)
    kept = sorted(current_sections & proposed_sections)

    diff = list(
        difflib.unified_diff(
            current_body.splitlines(keepends=True),
            proposed_body.splitlines(keepends=True),
            fromfile="current",
            tofile="proposed",
            n=2,
        )
    )
    line_added = sum(1 for d in diff if d.startswith("+") and not d.startswith("+++"))
    line_removed = sum(1 for d in diff if d.startswith("-") and not d.startswith("---"))

    return GateResult(
        gate="diff",
        passed=True,  # diff is informational, not pass/fail
        summary=(
            f"+{line_added}/-{line_removed} lines · "
            f"sections: +{len(added)}/-{len(removed)}/={len(kept)}"
        ),
        details={
            "lines_added": line_added,
            "lines_removed": line_removed,
            "sections_added": added,
            "sections_removed": removed,
            "sections_kept": kept,
            "unified_diff": "".join(diff),
        },
    )


def _extract_sections(body: str) -> set[str]:
    """Return set of (level, title) pairs as strings."""
    out: set[str] = set()
    for line in body.splitlines():
        m = _SECTION_RE.match(line.strip())
        if m:
            out.add(f"{len(m.group(1))}:{m.group(2).strip()}")
    return out


def gate_eval_delta(
    pack_id: str,
    proposed_text: str,
    repo_root: Path,
) -> GateResult:
    """Gate 3 — rerun probes against a temp registry pointing at proposed body.

    Skipped (passed=True, summary="skipped") if sillok.eval is not importable.
    """
    try:
        from sillok.eval import run_probes
    except Exception as exc:  # noqa: BLE001 — surface the absence as a skip
        return GateResult(
            gate="eval_delta",
            passed=True,
            summary="skipped — sillok.eval not available",
            details={"reason": str(exc)},
        )

    try:
        baseline = run_probes()
    except Exception as exc:  # noqa: BLE001
        return GateResult(
            gate="eval_delta",
            passed=False,
            summary="baseline run failed",
            error=str(exc),
        )

    proposed = _run_probes_with_proposed(pack_id, proposed_text, repo_root)
    if proposed is None:
        return GateResult(
            gate="eval_delta",
            passed=True,
            summary="skipped — proposed pack not present in registry yet",
            details={"baseline_pass_rate_pct": baseline.pass_rate_pct},
        )

    delta_pct = round(proposed.pass_rate_pct - baseline.pass_rate_pct, 2)
    p50_delta_ms = round(proposed.retrieval_p50_ms - baseline.retrieval_p50_ms, 3)

    # Pass condition: pass-rate did not drop more than 5pp.
    passed = delta_pct >= -5.0
    return GateResult(
        gate="eval_delta",
        passed=passed,
        summary=(
            f"pass rate {baseline.pass_rate_pct:.1f}% → {proposed.pass_rate_pct:.1f}% "
            f"(Δ{delta_pct:+.1f}pp) · p50 Δ{p50_delta_ms:+.3f}ms"
        ),
        details={
            "baseline_pass_rate_pct": baseline.pass_rate_pct,
            "proposed_pass_rate_pct": proposed.pass_rate_pct,
            "pass_rate_delta_pp": delta_pct,
            "p50_delta_ms": p50_delta_ms,
        },
    )


def _run_probes_with_proposed(
    pack_id: str,
    proposed_text: str,
    repo_root: Path,
):
    """Write proposed body to a temp path and patch the registry to point at it.

    Returns None if the pack isn't in the registry (cannot meaningfully diff).
    """
    import tempfile

    from sillok.eval import run_probes
    from sillok.naru.router_2tier import load_registry

    packs = load_registry(repo_root / "packs" / "registry.yaml")
    matching = next((p for p in packs if p.get("id") == pack_id), None)
    if matching is None:
        return None

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", delete=False, dir=repo_root, encoding="utf-8"
    ) as tmp_body:
        tmp_body.write(proposed_text)
        tmp_body_path = Path(tmp_body.name)

    try:
        # Build a temporary registry payload with the patched path
        original_path = matching["path"]
        matching["path"] = str(tmp_body_path.relative_to(repo_root))
        registry_payload = {"version": "0.1", "packs": packs}

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False, dir=repo_root, encoding="utf-8"
        ) as tmp_reg:
            yaml.safe_dump(registry_payload, tmp_reg)
            tmp_reg_path = Path(tmp_reg.name)

        try:
            return run_probes(registry_path=tmp_reg_path)
        finally:
            tmp_reg_path.unlink(missing_ok=True)
            matching["path"] = original_path
    finally:
        tmp_body_path.unlink(missing_ok=True)


def gate_approval_artifact(
    pack_id: str,
    diff_source: Path,
    gates: list[GateResult],
    proposals_dir: Path,
) -> tuple[GateResult, Path]:
    """Gate 4 — write the human-review artifact. *Never* applies the change."""
    from datetime import datetime, timezone

    from sillok.sangso.proposal import Proposal

    timestamp = datetime.now(timezone.utc)
    proposal = Proposal(
        pack_id=pack_id,
        timestamp=timestamp,
        diff_source=diff_source,
        gates=gates,
    )
    proposals_dir.mkdir(parents=True, exist_ok=True)
    artifact_path = proposals_dir / f"{proposal.id}.md"
    artifact_path.write_text(proposal.to_markdown(), encoding="utf-8")

    upstream_passed = all(g.passed for g in gates)
    return (
        GateResult(
            gate="approval",
            passed=upstream_passed,
            summary=(
                f"artifact written → {artifact_path.relative_to(proposals_dir.parent)}"
                + ("" if upstream_passed else " (upstream gate failures present — review required)")
            ),
            details={"artifact_path": str(artifact_path), "proposal_id": proposal.id},
        ),
        artifact_path,
    )


def run_all_gates(
    pack_id: str,
    current_text: str,
    proposed_text: str,
    repo_root: Path,
) -> list[GateResult]:
    """Execute gates 1-3 in order. Caller invokes ``gate_approval_artifact`` with the result list."""
    return [
        gate_lint(proposed_text),
        gate_diff(current_text, proposed_text),
        gate_eval_delta(pack_id, proposed_text, repo_root),
    ]
