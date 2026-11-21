# Sillok

> Productized LLM Wiki pattern + typed pack registry + proposal-only governance — a UNESCO Memory of the World Triple Anchor.

Sillok is a small, opinionated harness for running prompt-engineered workflows on top of your own knowledge base. It implements Andrej Karpathy's [LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) and adds the operational layers a real team needs: a typed pack registry, two-stage routing, proposal-only four-gate governance, multi-tenant overlays, and a multi-format auto-ingest pipeline.

## Top 10 features

1. **Multi-format Auto-Ingest RAG** — md / pdf / docx / xlsx / pptx / txt / hwpx; watch / cron / on-demand.
2. **Two-Stage Routing** — Tier 1 deterministic keyword match + Tier 2 pack-body load, with no LLM call; about 94% fewer pack-instruction tokens than loading every pack (ADR 0002).
3. **Typed Pack Registry + 5 Retrieval Plans** — `vault_first` / `with_fallback` / `recovery_first` / `dual_compare` / `no_corpus`.
4. **Proposal-Only 4-Gate Governance** — auto-growth never overwrites prompts directly.
5. **Multi-Tenant Overlay** — personal + team + per-client corpus layers.
6. **MCP Bridge** — Claude Code / Codex CLI / Gemini CLI / Cursor / Continue / Claude Desktop / Codex Desktop.
7. **Plugin System** — register external capabilities like packs.
8. **Eval Golden Probes + KPI Guard** — 30 router goldens + 17 RAG probes; CI-blocking.
9. **Cross-Tool Plan SSoT** — `docs/plans/<ID>-plan.md` shared across CLIs and IDEs.
10. **Failure Taxonomy + Replay Pointer** — every retro tagged with one of five failure classes plus replay coordinates.

See [Architecture](architecture/README.md) for the full module map.

## Status (2026-11-17)

The current release is **`0.4.1`** (alpha): 47 packs, the 2-tier router, proposal-only governance, a 10-probe eval gate, the MCP bridge, and four experimental, opt-in kernel managers. The per-feature live / partial / stub matrix is in [`STATUS.md`](https://github.com/sillok-os/sillok/blob/main/STATUS.md), release notes in [`CHANGELOG.md`](https://github.com/sillok-os/sillok/blob/main/CHANGELOG.md).

## Quick start

```bash
pip install sillok              # 0.4.1 · Python 3.11+
sillok route "Run a strategy audit for Acme with Porter five forces"
python -m sillok.eval run       # 10 golden probes
```

MCP bridge for Claude Code / Cursor: see [MCP quickstart](integrations/mcp-quickstart.md). Kernel managers (opt-in): see the README section *F. Kernel managers* and [`examples/kernel/`](https://github.com/sillok-os/sillok/tree/main/examples/kernel).

## License & community

- **Source code**: Apache License 2.0 — see [LICENSE](https://github.com/sillok-os/sillok/blob/main/LICENSE)
- **Starter atoms**: Creative Commons Attribution 4.0 (CC BY 4.0)
- **Trademarks**: see [NOTICE](https://github.com/sillok-os/sillok/blob/main/NOTICE)
- **Code of Conduct**: Contributor Covenant 2.1
- **Discussions**: <https://github.com/sillok-os/sillok/discussions>
- **Issues**: <https://github.com/sillok-os/sillok/issues>
