# SPDX-License-Identifier: Apache-2.0
"""sillok.sangso.canary — shadow vs prod KPI canary for the Shadow gate.

The governance lifecycle (see ``docs/governance/``) requires a proposal to pass
the **Shadow** stage — *"passes eval suite without regression"* — before it can
land. This module produces the evidence for that decision: record N eval rounds
in ``prod`` state and N in ``shadow`` state, then compare medians and render a
markdown evidence block with a pass/fail verdict against configurable
thresholds.

Design — provider-neutral, metric-agnostic:

- The caller supplies each round's metrics as a plain mapping (e.g.
  ``sillok.eval.EvalSummary.to_dict()``). There is **no hardcoded probe
  runner** — the canary never shells out, so it composes with any eval source.
- Aggregation is metric-agnostic: every numeric key present in the rows is
  summarised (median / mean / stdev / min / max). New metrics need no code
  change.
- The human controls the prod ↔ shadow toggle; the canary never applies a
  change. Evidence blocks are meant to be attached to a ``sangso`` proposal.

Example::

    from pathlib import Path
    from sillok.sangso.canary import record, compare, render_evidence, Threshold

    store = Path(".canary")
    for _ in range(5):
        record("prod", run_eval().to_dict(), store)
    # ... apply shadow change to your own environment ...
    for _ in range(5):
        record("shadow", run_eval().to_dict(), store)

    cmp = compare(load_rounds("prod", store), load_rounds("shadow", store))
    print(render_evidence(cmp, {
        "pass_rate_pct": Threshold(higher_is_better=True, max_regression=2.0),
        "retrieval_p50_ms": Threshold(higher_is_better=False, max_regression=50.0),
    }))
"""

from __future__ import annotations

import json
import statistics
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

Row = dict[str, Any]


@dataclass(frozen=True)
class Threshold:
    """Allowed regression for one metric.

    ``higher_is_better`` marks the metric direction (e.g. pass-rate is
    higher-better; latency is lower-better). ``max_regression`` is the largest
    tolerated move in the *bad* direction, as a non-negative magnitude.
    """

    higher_is_better: bool
    max_regression: float


@dataclass(frozen=True)
class Verdict:
    passed: bool
    violations: list[str]


def record(label: str, metrics: Mapping[str, Any], store_dir: Path) -> Path:
    """Append one round's ``metrics`` to ``<store_dir>/<label>.jsonl``."""
    store_dir.mkdir(parents=True, exist_ok=True)
    out = store_dir / f"{label}.jsonl"
    with out.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(dict(metrics), ensure_ascii=False) + "\n")
    return out


def load_rounds(label: str, store_dir: Path) -> list[Row]:
    """Load every recorded round for ``label`` (skips blank/corrupt lines)."""
    path = store_dir / f"{label}.jsonl"
    if not path.exists():
        return []
    rows: list[Row] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _numeric_keys(rows: Sequence[Row]) -> list[str]:
    keys: dict[str, None] = {}  # dict preserves first-seen order
    for row in rows:
        for key, value in row.items():
            if _is_number(value):
                keys.setdefault(key, None)
    return list(keys)


def aggregate(rows: Sequence[Row]) -> dict[str, dict[str, float]]:
    """Summarise every numeric metric across ``rows`` (metric-agnostic)."""
    summary: dict[str, dict[str, float]] = {}
    for key in _numeric_keys(rows):
        values = [float(row[key]) for row in rows if _is_number(row.get(key))]
        if not values:
            continue
        summary[key] = {
            "median": round(statistics.median(values), 4),
            "mean": round(statistics.mean(values), 4),
            "stdev": round(statistics.stdev(values), 4) if len(values) > 1 else 0.0,
            "min": round(min(values), 4),
            "max": round(max(values), 4),
            "n": float(len(values)),
        }
    return summary


def compare(prod_rows: Sequence[Row], shadow_rows: Sequence[Row]) -> dict[str, Any]:
    """Compare prod vs shadow; delta is ``shadow.median - prod.median`` per key."""
    prod = aggregate(prod_rows)
    shadow = aggregate(shadow_rows)
    delta = {
        key: round(shadow[key]["median"] - prod[key]["median"], 4) for key in prod if key in shadow
    }
    return {
        "prod": prod,
        "shadow": shadow,
        "delta_median": delta,
        "n_prod": len(prod_rows),
        "n_shadow": len(shadow_rows),
    }


def evaluate_verdict(
    comparison: Mapping[str, Any],
    thresholds: Mapping[str, Threshold],
) -> Verdict:
    """Fail if any threshold's metric regresses beyond its tolerance."""
    deltas: dict[str, float] = comparison.get("delta_median", {})
    violations: list[str] = []
    for metric, threshold in thresholds.items():
        delta = deltas.get(metric)
        if delta is None:
            continue
        regression = -delta if threshold.higher_is_better else delta
        if regression > threshold.max_regression:
            violations.append(
                f"{metric}: Δ={delta:+g} (regression {regression:+g} "
                f"> tolerance {threshold.max_regression:g})"
            )
    return Verdict(passed=not violations, violations=violations)


def render_evidence(
    comparison: Mapping[str, Any],
    thresholds: Mapping[str, Threshold] | None = None,
) -> str:
    """Render a markdown evidence block (table + verdict) for a proposal."""
    prod: dict[str, Any] = comparison.get("prod", {})
    shadow: dict[str, Any] = comparison.get("shadow", {})
    deltas: dict[str, float] = comparison.get("delta_median", {})

    lines = [
        f"### Shadow Canary Evidence — {date.today().isoformat()}",
        "",
        f"- rounds: prod n={comparison.get('n_prod', 0)} / "
        f"shadow n={comparison.get('n_shadow', 0)}",
        "",
        "| metric | prod median | shadow median | Δ |",
        "|---|---|---|---|",
    ]
    for metric, delta in deltas.items():
        prod_median = prod.get(metric, {}).get("median", "—")
        shadow_median = shadow.get(metric, {}).get("median", "—")
        lines.append(f"| `{metric}` | {prod_median} | {shadow_median} | {delta:+g} |")
    lines.append("")

    if thresholds:
        verdict = evaluate_verdict(comparison, thresholds)
        lines.append(f"**Verdict**: {'🟢 pass' if verdict.passed else '🔴 fail'}")
        for violation in verdict.violations:
            lines.append(f"- ⚠️ {violation}")
    else:
        lines.append("**Verdict**: — (no thresholds supplied — informational only)")
    lines.append("")
    return "\n".join(lines)
