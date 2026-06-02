"""Unit tests for sillok.yeonryun.coverage — coverage-gap clustering."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sillok.yeonryun import coverage


def _v2(message: str, selected: list[str], ts: str = "") -> dict:
    return {
        "trace_id": "t",
        "timestamp": ts,
        "input": {"message": message},
        "output": {"selected_pack_ids": selected, "selected_categories": []},
    }


def _legacy(message: str, selected: list[str], ts: str = "") -> dict:
    return {"timestamp": ts, "message": message, "selected_pack_ids": selected}


def test_extract_handles_v2_and_legacy_shapes() -> None:
    rows = [
        _v2("v2 empty one", []),
        _v2("v2 matched", ["pm-enhanced"]),
        _legacy("legacy empty two", []),
        _legacy("legacy matched", ["report-quality"]),
    ]
    empties = coverage.extract_empty_messages(rows)
    messages = {e.message for e in empties}
    assert messages == {"v2 empty one", "legacy empty two"}


def test_blank_message_is_skipped() -> None:
    assert coverage.extract_empty_messages([_v2("   ", [])]) == []


def test_window_filters_old_rows() -> None:
    now = datetime(2026, 6, 2, tzinfo=UTC)
    recent = (now - timedelta(days=2)).isoformat()
    old = (now - timedelta(days=40)).isoformat()
    rows = [_v2("recent gap", [], recent), _v2("old gap", [], old)]
    empties = coverage.extract_empty_messages(rows, window_days=7, now=now)
    assert [e.message for e in empties] == ["recent gap"]


def test_tokenize_korean_english_and_stopwords() -> None:
    toks = coverage.tokenize("배포 자동화 release pipeline 하는")
    assert "배포" in toks and "release" in toks
    assert "하는" not in toks  # default stopword filtered


def test_cluster_groups_similar_messages() -> None:
    msgs = [
        coverage.EmptyMessage(message="deploy release pipeline automation"),
        coverage.EmptyMessage(message="deploy release pipeline rollback"),
        coverage.EmptyMessage(message="deploy release pipeline canary"),
        coverage.EmptyMessage(message="totally unrelated cooking recipe"),
    ]
    clusters = coverage.cluster_gaps(msgs, min_cluster_size=3)
    assert len(clusters) == 1
    assert clusters[0].size == 3
    assert "deploy" in clusters[0].top_tokens
    assert clusters[0].trigger_candidates  # non-empty


def test_find_coverage_gaps_end_to_end() -> None:
    rows = [_v2(f"deploy release pipeline step {i}", []) for i in range(4)]
    rows.append(_v2("matched query", ["pm-enhanced"]))
    report = coverage.find_coverage_gaps(rows, min_cluster_size=3)
    assert report.total_empty_messages == 4
    assert len(report.clusters) == 1
    assert report.clusters[0].size == 4
