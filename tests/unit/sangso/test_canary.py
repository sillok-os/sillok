"""Unit tests for sillok.sangso.canary — shadow vs prod KPI canary."""

from __future__ import annotations

from pathlib import Path

from sillok.sangso import canary


def _metrics(pass_rate: float, p50: float) -> dict[str, float]:
    return {"pass_rate_pct": pass_rate, "retrieval_p50_ms": p50}


def test_record_and_load_roundtrip(tmp_path: Path) -> None:
    canary.record("prod", _metrics(90.0, 120.0), tmp_path)
    canary.record("prod", _metrics(92.0, 130.0), tmp_path)
    rows = canary.load_rounds("prod", tmp_path)
    assert len(rows) == 2
    assert rows[0]["pass_rate_pct"] == 90.0


def test_load_missing_label_is_empty(tmp_path: Path) -> None:
    assert canary.load_rounds("nope", tmp_path) == []


def test_aggregate_is_metric_agnostic() -> None:
    rows = [
        {"pass_rate_pct": 90.0, "retrieval_p50_ms": 100.0, "note": "ignored"},
        {"pass_rate_pct": 94.0, "retrieval_p50_ms": 140.0, "extra_metric": 5},
    ]
    agg = canary.aggregate(rows)
    assert agg["pass_rate_pct"]["median"] == 92.0
    assert agg["extra_metric"]["n"] == 1.0  # new metric needs no code change
    assert "note" not in agg  # non-numeric keys are dropped


def test_compare_delta_median() -> None:
    prod = [_metrics(90.0, 100.0), _metrics(90.0, 100.0)]
    shadow = [_metrics(93.0, 110.0), _metrics(93.0, 110.0)]
    cmp = canary.compare(prod, shadow)
    assert cmp["delta_median"]["pass_rate_pct"] == 3.0
    assert cmp["delta_median"]["retrieval_p50_ms"] == 10.0


def test_verdict_passes_within_tolerance() -> None:
    cmp = canary.compare([_metrics(90.0, 100.0)], [_metrics(89.0, 120.0)])
    thresholds = {
        "pass_rate_pct": canary.Threshold(higher_is_better=True, max_regression=2.0),
        "retrieval_p50_ms": canary.Threshold(higher_is_better=False, max_regression=50.0),
    }
    verdict = canary.evaluate_verdict(cmp, thresholds)
    assert verdict.passed
    assert verdict.violations == []


def test_verdict_fails_on_regression() -> None:
    cmp = canary.compare([_metrics(90.0, 100.0)], [_metrics(80.0, 100.0)])
    thresholds = {
        "pass_rate_pct": canary.Threshold(higher_is_better=True, max_regression=2.0),
    }
    verdict = canary.evaluate_verdict(cmp, thresholds)
    assert not verdict.passed
    assert any("pass_rate_pct" in v for v in verdict.violations)


def test_render_evidence_contains_table_and_verdict() -> None:
    cmp = canary.compare([_metrics(90.0, 100.0)], [_metrics(91.0, 100.0)])
    thresholds = {
        "pass_rate_pct": canary.Threshold(higher_is_better=True, max_regression=2.0),
    }
    md = canary.render_evidence(cmp, thresholds)
    assert "Shadow Canary Evidence" in md
    assert "| metric | prod median | shadow median | Δ |" in md
    assert "🟢 pass" in md


def test_render_evidence_without_thresholds_is_informational() -> None:
    cmp = canary.compare([_metrics(90.0, 100.0)], [_metrics(91.0, 100.0)])
    md = canary.render_evidence(cmp)
    assert "informational only" in md
