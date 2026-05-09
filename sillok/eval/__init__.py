"""sillok.eval — Golden probe runner + KPI guard (Gwageo).

Public surface:

- ``ProbeResult`` — single-probe outcome (pass/fail + metrics)
- ``EvalSummary`` — aggregate summary across probes
- ``run_probes`` — runs the bundled probe set against the live registry
- ``load_probes`` / ``load_baseline`` — fixture helpers

CLI: ``python -m sillok.eval run``.

See ``probes/probes.yaml`` for the v1 probe set (10 probes / 6 families).
"""
from __future__ import annotations

from .runner import (
    EvalSummary,
    ProbeResult,
    load_baseline,
    load_probes,
    run_probes,
)

__all__ = [
    "EvalSummary",
    "ProbeResult",
    "load_baseline",
    "load_probes",
    "run_probes",
]
