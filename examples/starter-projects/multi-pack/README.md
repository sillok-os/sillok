# multi-pack — chaining a domain pack with a quality guard

Sillok routes can compose multiple packs in a fixed order:
`domain → workflow → output-style → follow-up`, with `quality-guard`
attached when the message asks for evaluation. This example shows two
real-world multi-pack flows.

> **Status (2026-04-26)**: target experience for `0.1.0a1+`. Pack bodies
> are still stubs in the placeholder release; the routing decision is
> already correct.

## Scenario A — strategy audit + quality guard

Goal: produce a Lens-1 SaaS audit report and force the
`report-quality` pack onto the chain so claims are triangulated.

```bash
sillok route "[saas-audit] full 5-part audit on a B2B analytics SaaS, \
              with CRAAP + AIMQ + IQF gates on every claim"

# Expected (composition order = domain → workflow → quality-guard):
#   applied prompt packs:
#     consulting-saas-audit, report-quality
#   retrieval plan:       vault_first
#   confidence:           high
#   reason codes:         R1 (explicit-trigger), R3 (domain-keyword)
```

What you get back:

| Section | Source pack |
|---|---|
| Business + Tech + Market + Roadmap 5-part audit body | `consulting-saas-audit` |
| Claim Verification 5-stage table | both packs (`consulting-saas-audit` defines, `report-quality` checks) |
| Triangulation count gate (≥3 sources/claim) at the end | `report-quality` |

## Scenario B — risk register + executive 1-pager output style

Goal: build a PMBOK 8 risk register, then format the output for a
board-level reader.

```bash
sillok route "[risk] 10-column register for the Q4 platform release, \
              then a 1-pager exec brief"

# Expected:
#   applied prompt packs:
#     risk-uncertainty, exec-communication
#   retrieval plan:       vault_first
#   confidence:           medium
#   reason codes:         R1, R3, R4 (output-style hint)
```

| Section | Source pack |
|---|---|
| 10-column risk register with EMV / Monte Carlo math | `risk-uncertainty` |
| 1-pager Pyramid Principle restructure | `exec-communication` |

## Composition rules

```
                      domain   workflow  output-style  quality-guard  follow-up
              order:    1   →     2     →    3       +    4          →   5
       can repeat:    yes     yes        yes              no              yes
   typical count:    1-2     0-1        0-1              0-1             0-1
```

If two domain packs collide on the same intent, the higher `precedence`
wins. The full rule set lives in `sillok.naru.router_2tier` and the
declarative schema in `sillok.schemas.RegistryPackSchema`.

## How to verify

```bash
# Show every routing decision in JSON (auditable)
sillok route "..." --json --explain

# Replay against the goldens to confirm composition is stable
pytest tests/goldens/ -k "multi-pack"
```

## Non-goals for this example

- Multi-tenant overlays — see `examples/multi-tenant/`
- IDE / MCP integration — see `integrations/{claude-code,cursor,...}/`
- LLM execution — `--execute` requires an API key; this example only
  demonstrates routing decisions.
