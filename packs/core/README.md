# packs/core

Reserved for **first-party "core" packs** that are not domain-specific
(e.g. workflow-shortcuts, audience-aware-publish, output-style helpers
shared across domains).

The 10 starter packs in `0.1.0a0` are organized by usage:

  packs/methodology/    PMBOK / SAFe / ITIL / COSO / TOGAF (domain)
  packs/consulting/     Lens 0 strategy + Lens 1 SaaS audit
  packs/output-styles/  exec-communication

Cross-cutting helpers move to `packs/core/` as they land — see
upstream `aipm/prompts/system/registry.yaml` (workflow-shortcuts,
audience-aware-publish, etc.) for the candidates.

Until any of those land here, this directory is intentionally empty
of pack bodies; the registry has 0 entries pointing into it at
`0.1.0a0`.
