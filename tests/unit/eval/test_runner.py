"""Unit tests for sillok.eval — probe runner + Bond triangulation."""
from __future__ import annotations

import json

from sillok.eval import load_probes, run_probes
from sillok.eval.triangulation import check_triangulation


def test_load_bundled_probes_v1_shape() -> None:
    probes = load_probes()
    assert probes["version"] == 1
    assert "kpi_targets" in probes
    assert len(probes["families"]) == 6
    total = sum(len(f["queries"]) for f in probes["families"])
    assert total == 10, f"v1 ships exactly 10 probes (got {total})"


def test_run_probes_smoke_runs_against_live_registry() -> None:
    """Smoke test — every probe should produce at least one candidate."""
    summary = run_probes()
    assert summary.total == 10
    assert summary.citation_coverage_pct == 100.0, (
        f"every probe must produce ≥1 candidate; got {summary.citation_coverage_pct}%"
    )


def test_run_probes_pass_rate_is_high() -> None:
    """The bundled probes target the 10 starter packs; pass rate ≥ 80%.

    Tighter than 100% because trigger_signals were tuned for explicit tokens
    while the probes use natural-language phrasings.
    """
    summary = run_probes()
    assert summary.pass_rate_pct >= 80.0, (
        f"pass rate {summary.pass_rate_pct}% below 80% guard "
        f"(failed: {[r.probe_id for r in summary.per_probe if not r.matched]})"
    )


def test_run_probes_p50_under_target() -> None:
    """Tier-1 keyword match should be sub-100ms whole-set p50."""
    summary = run_probes()
    target = summary.kpi_targets.get("retrieval_p50_ms", 100)
    assert summary.retrieval_p50_ms <= target, (
        f"retrieval p50 {summary.retrieval_p50_ms}ms exceeds target {target}ms"
    )


def test_run_probes_family_filter() -> None:
    summary = run_probes(family_filter="pm-lifecycle")
    assert summary.total == 3
    assert all(r.family == "pm-lifecycle" for r in summary.per_probe)


def test_eval_summary_serializes_to_json() -> None:
    summary = run_probes(family_filter="output-style")
    payload = summary.to_dict()
    assert "per_probe" in payload
    json.dumps(payload)  # round-trip


def test_triangulation_passes_with_three_sources() -> None:
    text = """# Report

## Executive Summary

- Important claim with three sources [^1] [^2] [^3]

[^1]: Source A
[^2]: Source B
[^3]: Source C
"""
    result = check_triangulation(text, min_sources=3)
    assert result.total == 1
    assert result.passed == 1
    assert result.pass_rate_pct == 100.0


def test_triangulation_fails_below_three_sources() -> None:
    text = """# Report

## Executive Summary

- Bare claim with only one source [link](https://example.com)
- Another claim with no sources at all
"""
    result = check_triangulation(text, min_sources=3)
    assert result.total == 2
    assert result.passed == 0
    assert len(result.failures) == 2


def test_triangulation_skips_non_target_sections() -> None:
    text = """## Background

- This is background — no triangulation gate

## Executive Summary

- This is a claim that needs sources [a](x) [b](y) [c](z)
"""
    result = check_triangulation(text)
    assert result.total == 1, "only Executive Summary bullets should be scored"
