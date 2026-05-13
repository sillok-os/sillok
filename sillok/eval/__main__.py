"""sillok.eval.__main__ — CLI for the golden probe runner.

Sub-commands::

    python -m sillok.eval run [--family <id>] [--baseline <file.json>] [--json]
    python -m sillok.eval triangulate <report.md> [--strict]

``run`` exits non-zero when any probe fails (CI gate). ``triangulate`` checks a
markdown report against the Bond Evidence Principle #3 gate (≥3 sources per
claim) and exits non-zero in ``--strict`` mode on failure.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from sillok.eval.runner import EvalSummary, load_baseline, load_probes, run_probes


@click.group()
def cli() -> None:
    """Sillok eval — Gwageo runner."""


@cli.command("run")
@click.option(
    "--family",
    default=None,
    help="Restrict to a single family id (e.g., pm-lifecycle).",
)
@click.option(
    "--baseline",
    default=None,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Path to a prior run dump for regression diff.",
)
@click.option(
    "--probes",
    default=None,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Override probe set path (default: bundled probes/probes.yaml).",
)
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    help="Emit JSON summary on stdout (skips human report).",
)
def run(
    family: str | None,
    baseline: Path | None,
    probes: Path | None,
    as_json: bool,
) -> None:
    """Execute probes against the live registry; exit 1 on any failure."""
    probe_set = load_probes(probes) if probes else load_probes()
    summary = run_probes(probe_set=probe_set, family_filter=family)

    if as_json:
        click.echo(json.dumps(summary.to_dict(), indent=2))
    else:
        _human_report(summary)
        if baseline is not None:
            _baseline_diff(summary, load_baseline(baseline))

    if summary.failed > 0:
        sys.exit(1)


@cli.command("triangulate")
@click.argument(
    "report",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
)
@click.option(
    "--strict/--no-strict",
    default=False,
    show_default=True,
    help="Exit 1 on triangulation failure (CI gate).",
)
@click.option(
    "--min-sources",
    default=3,
    show_default=True,
    type=int,
    help="Bond Principle #3 — minimum sources per claim.",
)
def triangulate(report: Path, strict: bool, min_sources: int) -> None:
    """Run Bond Evidence Principles triangulation on a markdown report."""
    from sillok.eval.triangulation import check_triangulation

    result = check_triangulation(report.read_text(encoding="utf-8"), min_sources=min_sources)
    click.echo(
        f"Triangulation gate ≥{min_sources} sources/claim: "
        f"{result.passed}/{result.total} claims passed "
        f"({result.pass_rate_pct:.1f}%)"
    )
    for claim in result.failures[:10]:
        click.echo(f"  FAIL  L{claim.line}: {claim.text[:80]}… ({claim.source_count} sources)", err=True)
    if strict and result.failures:
        sys.exit(1)


def _human_report(s: EvalSummary) -> None:
    bar = "=" * 60
    click.echo(bar)
    click.echo(f"Sillok eval — {s.total} probes run")
    click.echo(bar)
    click.echo(f"Pass rate           : {s.passed}/{s.total} ({s.pass_rate_pct:.1f}%)")
    click.echo(f"Citation coverage   : {s.citation_coverage_pct:.1f}% (target: {s.kpi_targets.get('citation_coverage_pct', 100)}%)")
    click.echo(f"Retrieval p50 / p95 : {s.retrieval_p50_ms:.2f} ms / {s.retrieval_p95_ms:.2f} ms")
    if s.kpi_targets.get("retrieval_p50_ms"):
        click.echo(f"  target p50 ≤ {s.kpi_targets['retrieval_p50_ms']} ms — {'OK' if s.retrieval_p50_ms <= s.kpi_targets['retrieval_p50_ms'] else 'MISS'}")
    click.echo(bar)
    if s.failed > 0:
        click.echo("Failed probes:", err=True)
        for r in s.per_probe:
            if not r.matched:
                rank = f"rank={r.matched_rank}" if r.matched_rank else "no-match"
                click.echo(
                    f"  FAIL  [{r.family}/{r.probe_id}] {r.query!r} "
                    f"expected={r.expected_pack} {rank} top={r.candidate_pack_ids[:3]}",
                    err=True,
                )


def _baseline_diff(current: EvalSummary, baseline: dict) -> None:
    base_pass = baseline.get("pass_rate_pct", 0.0)
    delta = current.pass_rate_pct - base_pass
    arrow = "↑" if delta > 0 else ("↓" if delta < 0 else "·")
    click.echo(f"Baseline diff: {base_pass:.1f}% → {current.pass_rate_pct:.1f}% ({arrow}{abs(delta):.1f}pp)")


if __name__ == "__main__":
    cli()
