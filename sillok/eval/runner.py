"""sillok.eval.runner — Run probes against the live registry router.

For each probe, invoke ``naru.router_2tier.tier1_match`` against the live
``packs/registry.yaml`` and verify the expected pack appears either as top-1
(``require_top1: true``) or anywhere in the top-K candidate list.

KPIs reported per run:

- ``retrieval_p50_ms`` — median Tier-1 match latency across all probes
- ``citation_coverage_pct`` — share of probes that produced ≥1 candidate
- ``pass_rate_pct`` — share of probes whose expected pack was matched
- ``per_probe`` — full per-probe detail
"""
from __future__ import annotations

import statistics
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml

from sillok.naru.router_2tier import load_registry, tier1_match

PROBES_DEFAULT = Path(__file__).parent / "probes" / "probes.yaml"


@dataclass
class ProbeResult:
    family: str
    probe_id: str
    query: str
    expected_pack: str
    require_top1: bool
    top_k: int
    matched: bool
    matched_rank: int | None  # 1-based rank if matched, None otherwise
    candidate_pack_ids: list[str]
    elapsed_ms: float


@dataclass
class EvalSummary:
    total: int
    passed: int
    failed: int
    pass_rate_pct: float
    citation_coverage_pct: float
    retrieval_p50_ms: float
    retrieval_p95_ms: float
    per_probe: list[ProbeResult] = field(default_factory=list)
    kpi_targets: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["per_probe"] = [asdict(p) for p in self.per_probe]
        return d


def load_probes(path: Path = PROBES_DEFAULT) -> dict[str, Any]:
    """Load the YAML probe set."""
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def load_baseline(path: Path) -> dict[str, Any]:
    """Load a previous run dump for diffing."""
    import json

    return json.loads(Path(path).read_text(encoding="utf-8"))


def _flatten_probes(
    probe_set: dict[str, Any],
    family_filter: str | None = None,
) -> list[tuple[str, dict[str, Any]]]:
    """Yield (family_id, probe) tuples, optionally filtered by family id."""
    out: list[tuple[str, dict[str, Any]]] = []
    for family in probe_set.get("families", []):
        family_id = family["id"]
        if family_filter and family_id != family_filter:
            continue
        for probe in family.get("queries", []):
            out.append((family_id, probe))
    return out


def run_probes(
    probe_set: dict[str, Any] | None = None,
    registry_path: Path | None = None,
    family_filter: str | None = None,
) -> EvalSummary:
    """Execute every probe in the set; return aggregate summary."""
    if probe_set is None:
        probe_set = load_probes()
    packs = (
        load_registry(registry_path)
        if registry_path
        else load_registry()
    )

    results: list[ProbeResult] = []
    elapsed_samples: list[float] = []

    for family_id, probe in _flatten_probes(probe_set, family_filter):
        top_k = int(probe.get("top_k", 3))
        require_top1 = bool(probe.get("require_top1", False))
        expected = probe["expected_pack"]

        t0 = time.perf_counter()
        candidates = tier1_match(probe["query"], packs, top_k=top_k)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        elapsed_samples.append(elapsed_ms)

        candidate_ids = [c.get("id") or c.get("pack_id") for c in candidates]
        matched_rank: int | None = None
        for idx, candidate in enumerate(candidates, start=1):
            cid = candidate.get("id") or candidate.get("pack_id")
            if cid == expected:
                matched_rank = idx
                break

        if require_top1:
            matched = matched_rank == 1
        else:
            matched = matched_rank is not None and matched_rank <= top_k

        results.append(
            ProbeResult(
                family=family_id,
                probe_id=probe["id"],
                query=probe["query"],
                expected_pack=expected,
                require_top1=require_top1,
                top_k=top_k,
                matched=matched,
                matched_rank=matched_rank,
                candidate_pack_ids=[c for c in candidate_ids if c is not None],
                elapsed_ms=round(elapsed_ms, 3),
            )
        )

    total = len(results)
    passed = sum(1 for r in results if r.matched)
    failed = total - passed
    cited = sum(1 for r in results if r.candidate_pack_ids)

    p50 = statistics.median(elapsed_samples) if elapsed_samples else 0.0
    p95 = (
        sorted(elapsed_samples)[int(0.95 * (len(elapsed_samples) - 1))]
        if elapsed_samples
        else 0.0
    )

    return EvalSummary(
        total=total,
        passed=passed,
        failed=failed,
        pass_rate_pct=round(100.0 * passed / total, 2) if total else 0.0,
        citation_coverage_pct=round(100.0 * cited / total, 2) if total else 0.0,
        retrieval_p50_ms=round(p50, 3),
        retrieval_p95_ms=round(p95, 3),
        per_probe=results,
        kpi_targets=probe_set.get("kpi_targets", {}),
    )
