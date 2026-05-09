"""sillok.sangso — Proposal-only 4-gate governance.

Top 10 Feature #4: hard guard against prompt drift and corpus poisoning.
Auto-growth from ``sillok.eval`` and telemetry **never** overwrites packs
directly — every change first lands as a proposal artifact in ``proposals/``
and must pass through:

1. Lint    — schema / frontmatter / body length / link integrity
2. Diff    — 3-way diff vs current; structural change summary
3. Eval Δ  — rerun probes; report pass-rate and p50 deltas
4. Approval — write artifact for human review (NO auto-merge)

CLI: ``python -m sillok.sangso``.
"""
from __future__ import annotations

from .gates import (
    GateResult,
    gate_approval_artifact,
    gate_diff,
    gate_eval_delta,
    gate_lint,
    run_all_gates,
)
from .proposal import Proposal, ProposalSummary

__all__ = [
    "GateResult",
    "Proposal",
    "ProposalSummary",
    "gate_approval_artifact",
    "gate_diff",
    "gate_eval_delta",
    "gate_lint",
    "run_all_gates",
]
