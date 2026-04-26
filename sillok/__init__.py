"""Sillok — Productized LLM Wiki pattern + typed pack registry + proposal-only governance.

Top-level package. Real implementation lands as 0.1.0a1; current 0.0.1
on PyPI is a namespace placeholder. Use submodules:

  sillok.naru        — two-stage routing (Top 10 Feature #2)
  sillok.bongsu      — five retrieval plans (Feature #3)
  sillok.jikji       — typed pack registry (Feature #3)
  sillok.sangso      — proposal-only 4-gate governance (Feature #4)
  sillok.telemetry   — observability (Feature #10 — Sagwan)
  sillok.schemas     — Pydantic schemas (Beopjeon)
  sillok.eval        — golden probes + KPI (Feature #8 — Gwageo)
  sillok.cli         — command-line entry point (Madang)
  sillok.plugins     — plugin system (Feature #7 — Dure)

See README.md for the Top 10 features overview.
"""

__version__ = "0.1.0a0.dev0"
__all__ = ["__version__"]
