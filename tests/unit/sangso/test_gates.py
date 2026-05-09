"""Unit tests for sillok.sangso — 4-gate proposal governance."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from sillok.sangso.gates import (
    gate_approval_artifact,
    gate_diff,
    gate_eval_delta,
    gate_lint,
    run_all_gates,
)
from sillok.sangso.proposal import Proposal


# ---------------------------------------------------------------------------
# Gate 1 — Lint
# ---------------------------------------------------------------------------

def _make_pack_text(*, body_lines: int = 250, broken_link: bool = False, missing_field: bool = False) -> str:
    front_lines = [
        "---",
        "id: test-pack",
        "title: Test Pack",
        "category: domain",
        "sub_category: methodology",
        "version: 0.1.0",
        "license: Apache-2.0",
        "---",
        "",
        "# Test Pack",
        "",
    ]
    if missing_field:
        front_lines = [line for line in front_lines if not line.startswith("license:")]
    body = ["body line {}".format(i) for i in range(body_lines)]
    if broken_link:
        body.append("[broken]() and [ok](https://example.com)")
    return "\n".join(front_lines + body)


def test_gate_lint_passes_on_well_formed_pack() -> None:
    result = gate_lint(_make_pack_text())
    assert result.gate == "lint"
    assert result.passed is True
    assert result.error is None
    assert result.details["body_lines"] >= 200


def test_gate_lint_fails_on_short_body() -> None:
    result = gate_lint(_make_pack_text(body_lines=50))
    assert result.passed is False
    assert "lines" in (result.error or "")
    assert result.details["body_lines"] < 200


def test_gate_lint_fails_on_missing_required_field() -> None:
    result = gate_lint(_make_pack_text(missing_field=True))
    assert result.passed is False
    assert "license" in (result.error or "")


def test_gate_lint_fails_on_broken_link() -> None:
    result = gate_lint(_make_pack_text(broken_link=True))
    assert result.passed is False
    assert "broken markdown link" in (result.error or "")


def test_gate_lint_fails_on_no_frontmatter() -> None:
    result = gate_lint("# Just a heading, no frontmatter")
    assert result.passed is False
    assert "frontmatter" in (result.error or "").lower()


# ---------------------------------------------------------------------------
# Gate 2 — Diff
# ---------------------------------------------------------------------------

def test_gate_diff_reports_section_changes() -> None:
    current = "---\nid: x\n---\n\n# Title\n\n## Section A\n\nbody\n"
    proposed = "---\nid: x\n---\n\n# Title\n\n## Section A\n\nbody\n\n## Section B\n\nnew\n"
    result = gate_diff(current, proposed)
    assert result.passed is True  # diff is informational
    assert "+1" in result.summary
    assert "2:Section B" in result.details["sections_added"]


def test_gate_diff_handles_identical_input() -> None:
    text = "---\nid: x\n---\n\n# Title\n\nsame body\n"
    result = gate_diff(text, text)
    assert result.passed is True
    assert result.details["lines_added"] == 0
    assert result.details["lines_removed"] == 0


# ---------------------------------------------------------------------------
# Gate 3 — Eval delta (graceful skip when sillok.eval absent)
# ---------------------------------------------------------------------------

def test_gate_eval_delta_runs_or_skips(tmp_path: Path) -> None:
    """The gate must not crash whether or not sillok.eval is importable."""
    proposed = _make_pack_text()
    result = gate_eval_delta("nonexistent-pack-xyz", proposed, repo_root=tmp_path)
    assert result.gate == "eval_delta"
    # Either skipped (no sillok.eval / pack not in registry) or ran (pack ID was in registry):
    # both must be passed=True for an unrelated pack.
    assert result.passed is True


# ---------------------------------------------------------------------------
# Gate 4 — Approval artifact (no auto-merge)
# ---------------------------------------------------------------------------

def test_gate_approval_writes_artifact(tmp_path: Path) -> None:
    proposals_dir = tmp_path / "proposals"
    diff_path = tmp_path / "diff.md"
    diff_path.write_text(_make_pack_text(), encoding="utf-8")

    earlier_gates = [
        gate_lint(_make_pack_text()),
        gate_diff(_make_pack_text(), _make_pack_text()),
    ]
    approval, artifact_path = gate_approval_artifact(
        pack_id="test-pack",
        diff_source=diff_path,
        gates=earlier_gates,
        proposals_dir=proposals_dir,
    )

    assert artifact_path.exists()
    assert approval.passed is True
    text = artifact_path.read_text(encoding="utf-8")
    assert "proposal_id:" in text
    assert "pack_id: test-pack" in text
    assert "## Gate Results" in text


def test_gate_approval_marks_failure_when_upstream_failed(tmp_path: Path) -> None:
    proposals_dir = tmp_path / "proposals"
    diff_path = tmp_path / "diff.md"
    diff_path.write_text(_make_pack_text(), encoding="utf-8")

    earlier_gates = [
        gate_lint("# no frontmatter"),  # fails
    ]
    approval, _ = gate_approval_artifact(
        pack_id="bad-pack",
        diff_source=diff_path,
        gates=earlier_gates,
        proposals_dir=proposals_dir,
    )
    assert approval.passed is False
    assert "review required" in approval.summary


# ---------------------------------------------------------------------------
# Round-trip — Proposal serialization
# ---------------------------------------------------------------------------

def test_proposal_round_trip_through_disk(tmp_path: Path) -> None:
    diff_path = tmp_path / "x.md"
    diff_path.write_text(_make_pack_text(), encoding="utf-8")
    p = Proposal(
        pack_id="round-trip",
        timestamp=datetime(2026, 5, 9, 12, 0, 0, tzinfo=timezone.utc),
        diff_source=diff_path,
        gates=[gate_lint(_make_pack_text())],
    )
    artifact = tmp_path / f"{p.id}.md"
    artifact.write_text(p.to_markdown(), encoding="utf-8")
    summary = Proposal.load(artifact)
    assert summary.pack_id == "round-trip"
    assert summary.upstream_passed is True
    assert summary.id == p.id


# ---------------------------------------------------------------------------
# Auto-merge guard — must NOT exist
# ---------------------------------------------------------------------------

def test_no_force_flag_in_accept_command() -> None:
    """The accept sub-command must not expose any --force / --yes / -y flag."""
    from sillok.sangso.__main__ import accept

    flag_names: list[str] = []
    for param in accept.params:
        flag_names.extend(param.opts)
    forbidden = {"--force", "--yes", "-y", "--no-confirm"}
    intersection = set(flag_names) & forbidden
    assert not intersection, f"forbidden flags exposed by accept: {intersection}"


def test_run_all_gates_returns_three_results(tmp_path: Path) -> None:
    current = _make_pack_text()
    proposed = _make_pack_text(body_lines=300)
    results = run_all_gates("test-pack", current, proposed, repo_root=tmp_path)
    assert len(results) == 3
    assert [r.gate for r in results] == ["lint", "diff", "eval_delta"]
