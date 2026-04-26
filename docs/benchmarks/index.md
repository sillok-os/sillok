# Benchmarks

Sillok ships built-in benchmarks for routing accuracy and RAG retrieval
KPIs. Results land in `benchmark/results/` per release.

## What gets benchmarked

| Suite | What it measures | Target |
|---|---|---|
| Router goldens | Pack-selection accuracy on 30 hand-curated cases | ≥ 95% match rate |
| RAG probes | Retrieval recall + citation coverage on 17 probes / 6 families | citation 100%, p50 ≤ 10s |
| 2-tier saving | Token cost reduction vs. naive full-load | ≥ 30% reduction |
| Cold-start ingest | Time to bootstrap a 1k-file vault | ≤ 5 min on M2-class hardware |

Targets above mirror the KPI block in `tests/probes/probes.yaml`.

## Running locally

```bash
# Full eval suite (when wired in F0.7 step 2)
sillok gwageo run --suite all --baseline last

# Just the goldens
pytest tests/goldens/

# 2-tier saving snapshot
python -m sillok.naru.router_2tier --breakdown
```

## CI

`.github/workflows/eval.yml` runs the suites on every PR and nightly.
Currently warn-only; flips to blocking in PR-B (Phase 1) once 4 weeks
of warn-only data have accumulated and the goldens are agreed-stable.

## Results format

Each CI run writes a JSON record under `benchmark/results/<date>-<sha>.json`:

```json
{
  "run_id": "2026-04-26-abc123",
  "router_goldens": { "passed": 30, "total": 30, "delta": 0 },
  "rag_probes": { "citation_pct": 100.0, "p50_seconds": 8.2 },
  "tier_saving_pct": 88.4,
  "cold_start_seconds": 287
}
```

## See also

- [Architecture](../architecture/README.md)
- [Governance — proposal pipeline](../governance/) for how regressions
  block merges
