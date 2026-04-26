# Sillok

> Productized LLM Wiki pattern + typed pack registry + proposal-only governance — a UNESCO Memory of the World Triple Anchor.

Sillok is a small, opinionated harness for running prompt-engineered workflows on top of your own knowledge base. It implements Andrej Karpathy's [LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) and adds the operational layers a real team needs: a typed pack registry, two-stage routing, proposal-only four-gate governance, multi-tenant overlays, and a multi-format auto-ingest pipeline.

## Top 10 features

1. **Multi-format Auto-Ingest RAG** — md / pdf / docx / xlsx / pptx / txt / hwpx; watch / cron / on-demand.
2. **Two-Stage Routing** — Tier 1 keyword match + Tier 2 LLM intent; ~97% token reduction.
3. **Typed Pack Registry + 5 Retrieval Plans** — `vault_first` / `with_fallback` / `recovery_first` / `dual_compare` / `no_corpus`.
4. **Proposal-Only 4-Gate Governance** — auto-growth never overwrites prompts directly.
5. **Multi-Tenant Overlay** — personal + team + per-client corpus layers.
6. **MCP Bridge** — Claude Code / Codex CLI / Gemini CLI / Cursor / Continue / Claude Desktop / Codex Desktop.
7. **Plugin System** — register external capabilities like packs.
8. **Eval Golden Probes + KPI Guard** — 30 router goldens + 17 RAG probes; CI-blocking.
9. **Cross-Tool Plan SSoT** — `docs/plans/<ID>-plan.md` shared across CLIs and IDEs.
10. **Failure Taxonomy + Replay Pointer** — every retro tagged with one of five failure classes plus replay coordinates.

See [Architecture](architecture/README.md) for the full module map.

## Status (2026-04-26)

Sillok is in **Phase 0** (Foundation). The current PyPI release is `0.0.1`, a namespace placeholder; the first functional alpha will be `0.1.0a1` once Phase 0 cherry-pick (F0.2 ~ F0.11) is complete and exited.

| Phase | Status |
|---|---|
| Phase 0 — Foundation (cherry-pick + governance + skeleton) | in progress |
| Phase 1 — Eval Discipline (CI-blocking eval, DSPy/GEPA) | next |
| Phase 2 — Production Polish (cost telemetry, OTel, multi-format ingest) | future |
| Phase 3 — Strategic (preprint, community, multi-tenant) | future |

## Quick start

```bash
pip install "sillok==0.0.1"   # placeholder reserve only — wait for 0.1.0a1
```

Once `0.1.0a1` ships:

```bash
pip install sillok
sillok init
sillok route "Draft a Q3 strategy report"
```

## License & community

- **Source code**: Apache License 2.0 — see [LICENSE](https://github.com/sillok-os/sillok/blob/main/LICENSE)
- **Starter atoms**: Creative Commons Attribution 4.0 (CC BY 4.0)
- **Trademarks**: see [NOTICE](https://github.com/sillok-os/sillok/blob/main/NOTICE)
- **Code of Conduct**: Contributor Covenant 2.1
- **Discussions**: <https://github.com/sillok-os/sillok/discussions>
- **Issues**: <https://github.com/sillok-os/sillok/issues>
