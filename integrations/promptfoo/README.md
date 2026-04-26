# integrations/promptfoo

Promptfoo provider that wraps Sillok routing + execution for
black-box prompt evaluation.

## Status

| | |
|---|---|
| Schedule | Phase 1 (PR-B — Eval CI blocking) |
| Current | 🟡 placeholder — Sillok ships its own goldens / probes (`tests/goldens/`, `tests/probes/`); Promptfoo gives users a richer eval UX on top |
| Activation | when `sillok-promptfoo` is published as a separate PyPI package |

## What this integration adds (target experience)

Promptfoo is a popular OSS prompt-eval tool with a YAML test-spec
format and a web UI. This bridge lets Promptfoo treat Sillok as a
provider so its eval matrix can include Sillok routes.

```yaml
# promptfooconfig.yaml (target)
providers:
  - id: sillok
    config:
      registry: packs/registry.yaml
      execute: false      # routing-only assertion
  - id: openai:gpt-4o
    config: { temperature: 0 }

tests:
  - vars:
      message: "[risk] 10-column register"
    assert:
      - type: equals
        value: "applied prompt packs: risk-uncertainty"
```

## Why this matters

| Concern | Sillok native (today) | Promptfoo on top of Sillok (target) |
|---|---|---|
| 30 router goldens regression gate | `tests/goldens/router-golden.jsonl` | same goldens, plus side-by-side diff against any other provider |
| 17 RAG probes KPI guard | `tests/probes/probes.yaml` | same probes, with Promptfoo's pass/fail UI |
| 1-off ad-hoc test | `pytest -k <id>` | `promptfoo eval -t <case>` with rich diff |

## Configuration knobs (planned)

```toml
# .sillok/config.toml
[integrations.promptfoo]
enabled = false
config_path = "promptfooconfig.yaml"
shadow_against = "openai:gpt-4o"
```

## Today

`tests/goldens/router-golden.jsonl` and `tests/probes/probes.yaml`
already validate without Promptfoo — see `.github/workflows/eval.yml`
(currently warn-only, becomes blocking in PR-B).

## Non-goals

- Promptfoo plug-in distribution — separate concern.
- Comparing Sillok to other prompt routers — Promptfoo can do this
  externally; not the bridge's job.
