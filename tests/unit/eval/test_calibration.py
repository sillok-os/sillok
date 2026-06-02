"""Unit tests for sillok.eval.calibration — routing confidence calibration."""

from __future__ import annotations

from sillok.eval import calibration as cal


def _case(exp_c: float, obs_c: float, exp_p: str, obs_p: str) -> cal.CalibrationCase:
    return cal.CalibrationCase(
        expected_confidence=exp_c,
        observed_confidence=obs_c,
        expected_top_pack=exp_p,
        observed_top_pack=obs_p,
    )


def test_brier_score_perfect_is_zero() -> None:
    cases = [_case(0.9, 0.9, "a", "a"), _case(0.5, 0.5, "b", "b")]
    assert cal.brier_score(cases) == 0.0


def test_brier_score_known_value() -> None:
    # errors: (0.8-1.0)^2=0.04, (0.6-0.4)^2=0.04 -> mean 0.04
    cases = [_case(1.0, 0.8, "a", "a"), _case(0.4, 0.6, "b", "b")]
    assert abs(cal.brier_score(cases) - 0.04) < 1e-9


def test_top_pack_match_rate() -> None:
    cases = [_case(0.9, 0.9, "a", "a"), _case(0.9, 0.9, "b", "c")]
    assert cal.top_pack_match_rate(cases) == 0.5


def test_empty_cases_are_safe() -> None:
    assert cal.brier_score([]) == 0.0
    assert cal.top_pack_match_rate([]) == 0.0


def test_calibrate_passes_when_within_thresholds() -> None:
    cases = [_case(0.9, 0.9, "a", "a") for _ in range(20)]
    report = cal.calibrate(cases)
    assert report.verdict.overall_pass
    assert report.brier_score == 0.0
    assert report.top_pack_match_rate == 1.0
    assert report.pack_drift_count == 0


def test_calibrate_fails_on_drift_and_miscalibration() -> None:
    cases = [_case(1.0, 0.0, "a", "b") for _ in range(10)]
    report = cal.calibrate(cases)
    assert not report.verdict.overall_pass
    assert not report.verdict.brier_pass  # brier=1.0 > 0.05
    assert not report.verdict.top_match_pass  # match rate 0
    assert report.pack_drift_count == 10


def test_cases_from_routing_adapter() -> None:
    golden = [
        {"input": "deploy the release", "expected_confidence": 0.9, "expected_top_pack": "release"},
        {"input": "audit the issues", "expected_confidence": 0.8, "expected_top_pack": "pm"},
    ]

    def route(message: str) -> tuple[float, str | None]:
        if "release" in message:
            return 0.91, "release"
        return 0.5, "other"

    cases = cal.cases_from_routing(golden, route)
    assert len(cases) == 2
    assert cases[0].observed_top_pack == "release"
    assert cases[1].observed_top_pack == "other"  # mismatch vs expected "pm"
    report = cal.calibrate(cases)
    assert report.pack_drift_count == 1
