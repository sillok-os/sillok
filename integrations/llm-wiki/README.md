# integrations/llm-wiki

Optional bridge to an **archived llm-wiki** corpus (Karpathy's 3-layer
pattern, applied to a separate snapshot kept around for historical
recovery purposes).

## Status

| | |
|---|---|
| Schedule | Phase 2 — gates `dual_compare` and `llmwiki_recovery_first` retrieval plans |
| Current | 🟡 placeholder — the retrieval-plan IDs exist in `packs/registry.yaml` but no live implementation |
| Activation | when at least one starter pack declares `corpus_affinity.retrieval_plan: llmwiki_recovery_first` and an llm-wiki snapshot directory is configured |

## Why a separate llm-wiki repo

Sillok's primary corpus is **vault-resident** (see ADR 0001 / D3 and
the K-6 30-hour ablation in the public README). However, a frozen
llm-wiki snapshot has two narrow uses:

1. **Historical recovery** — when a methodology canon was once captured
   in an llm-wiki note and is no longer in the live vault.
2. **Dual-compare evaluation** — running the same query against vault
   and the snapshot to surface the structural-coverage gap.

These use cases are exactly what the `llmwiki_recovery_first` and
`dual_compare` retrieval plans (declared in `packs/registry.yaml`)
target.

## Configuration knobs (planned)

```toml
# .sillok/config.toml
[integrations.llm-wiki]
enabled = false
snapshot_dir = "~/Library/Sillok/llm-wiki-snapshot-2026-01"
read_only = true
```

## Today

This integration is intentionally inert. Routes that select a pack
declaring `llmwiki_recovery_first` will currently get a
`no-corpus` fallback noted in telemetry's `knowledge_gap_label` field
(`"no-hits"`). That signal feeds the proposal pipeline (Top 10 Feature
#4) so retrieval gaps surface as candidate proposals — even before the
bridge is wired.

## Non-goals

- Building or maintaining the snapshot — that is a separate operational
  concern outside this integration.
- Writing back to llm-wiki — the bridge is read-only by design.
