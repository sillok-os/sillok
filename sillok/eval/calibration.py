# SPDX-License-Identifier: Apache-2.0
"""sillok.eval.calibration — routing confidence calibration (Brier score).

A well-behaved router does not only pick the right pack; its reported
``confidence`` should *track reality*. This module measures that with two
metrics over a labelled calibration set:

- **Brier score** — mean squared error between observed and expected
  confidence (lower is better; 0 is perfect).
- **top-pack match rate** — fraction of cases whose top selected pack equals
  the expected one.

Design — provider-neutral, pure:

- The core works on pre-paired :class:`CalibrationCase` values (expected vs
  observed). It never invokes a router, so it has no dependency on any
  particular routing implementation and is trivially testable.
- :func:`cases_from_routing` is an optional adapter: pass golden rows plus a
  ``route_fn`` callable and it produces the paired cases for you.

Example::

    from sillok.eval.calibration import calibrate, cases_from_routing

    def route(message: str) -> tuple[float, str | None]:
        result = my_router(message)
        return result.confidence, (result.pack_ids[0] if result.pack_ids else None)

    cases = cases_from_routing(golden_rows, route)
    report = calibrate(cases)
    assert report.verdict.overall_pass
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass, field
from typing import Any

#: Default regression thresholds (override per call).
DEFAULT_BRIER_MAX = 0.05
DEFAULT_TOP_MATCH_MIN = 0.95


@dataclass(frozen=True)
class CalibrationCase:
    """One labelled case: what the router *should* say vs what it *did* say."""

    expected_confidence: float
    observed_confidence: float
    expected_top_pack: str | None = None
    observed_top_pack: str | None = None


@dataclass(frozen=True)
class CalibrationVerdict:
    brier_pass: bool
    top_match_pass: bool
    overall_pass: bool


@dataclass
class CalibrationReport:
    n_cases: int
    brier_score: float
    top_pack_match_rate: float
    pack_drift_count: int
    brier_max: float
    top_match_min: float
    verdict: CalibrationVerdict
    per_case_squared_error: list[float] = field(default_factory=list)


def brier_score(cases: Sequence[CalibrationCase]) -> float:
    """Mean squared error between observed and expected confidence."""
    if not cases:
        return 0.0
    total = sum((c.observed_confidence - c.expected_confidence) ** 2 for c in cases)
    return total / len(cases)


def top_pack_match_rate(cases: Sequence[CalibrationCase]) -> float:
    """Fraction of cases whose observed top pack equals the expected one."""
    if not cases:
        return 0.0
    matches = sum(1 for c in cases if c.observed_top_pack == c.expected_top_pack)
    return matches / len(cases)


def calibrate(
    cases: Sequence[CalibrationCase],
    *,
    brier_max: float = DEFAULT_BRIER_MAX,
    top_match_min: float = DEFAULT_TOP_MATCH_MIN,
) -> CalibrationReport:
    """Score a calibration set and emit a pass/fail verdict."""
    squared_errors = [round((c.observed_confidence - c.expected_confidence) ** 2, 6) for c in cases]
    brier = brier_score(cases)
    top_rate = top_pack_match_rate(cases)
    drift = sum(1 for c in cases if c.observed_top_pack != c.expected_top_pack)

    brier_pass = brier <= brier_max
    top_match_pass = top_rate >= top_match_min
    return CalibrationReport(
        n_cases=len(cases),
        brier_score=round(brier, 6),
        top_pack_match_rate=round(top_rate, 4),
        pack_drift_count=drift,
        brier_max=brier_max,
        top_match_min=top_match_min,
        verdict=CalibrationVerdict(
            brier_pass=brier_pass,
            top_match_pass=top_match_pass,
            overall_pass=brier_pass and top_match_pass,
        ),
        per_case_squared_error=squared_errors,
    )


def cases_from_routing(
    golden: Iterable[dict[str, Any]],
    route_fn: Callable[[str], tuple[float, str | None]],
) -> list[CalibrationCase]:
    """Build paired cases by running ``route_fn`` over labelled golden rows.

    Each golden row is a mapping with ``input`` (the message), and the labels
    ``expected_confidence`` and ``expected_top_pack``. ``route_fn`` returns
    ``(observed_confidence, observed_top_pack)`` for a message.
    """
    cases: list[CalibrationCase] = []
    for row in golden:
        message = str(row.get("input", ""))
        observed_confidence, observed_top = route_fn(message)
        cases.append(
            CalibrationCase(
                expected_confidence=float(row.get("expected_confidence", 0.0)),
                observed_confidence=float(observed_confidence),
                expected_top_pack=row.get("expected_top_pack"),
                observed_top_pack=observed_top,
            )
        )
    return cases
