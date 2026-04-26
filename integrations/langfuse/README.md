# integrations/langfuse

OpenTelemetry exporter that ships Sillok telemetry rows to Langfuse.

## Status

| | |
|---|---|
| Schedule | Phase 2 (PR-G — OTel / Langfuse adapter) |
| Current | 🟡 placeholder — Sillok telemetry already follows an OTEL-compatible schema (`sillok.schemas.TelemetryRow`); the bridge handles span emission |
| Activation | when `pip install sillok[otel]` is supported and `SILLOK_OTEL=1` is set |

## What this integration adds (target experience)

Langfuse is an OSS LLM-observability platform with rich trace UI.
Sillok already produces rows in an OTEL-compatible shape — this bridge
just emits them as proper OTel spans so Langfuse can render them
end-to-end.

| Sillok row field | OTel span attribute | Langfuse view |
|---|---|---|
| `trace_id` | `trace.id` | trace ID |
| `event_name` (`sillok.route`) | span name | "Routing decision" |
| `input.message_hash` | `sillok.input.message_hash` | privacy-preserving message ref |
| `output.applied_prompt_packs_line` | `sillok.output.packs_line` | which packs fired |
| `metadata.registry_version` | `sillok.metadata.registry_sha` | which registry version was active |
| `latency_ms` | span duration | latency histogram |
| `tokens_in / tokens_out / usd_cost` | OTel `gen_ai.usage.*` | cost dashboards |

## Configuration knobs (planned)

```bash
export SILLOK_OTEL=1
export OTEL_EXPORTER_OTLP_ENDPOINT="https://cloud.langfuse.com/api/otel/v1/traces"
export OTEL_EXPORTER_OTLP_HEADERS="authorization=Basic <base64>"
```

```toml
# .sillok/config.toml
[integrations.langfuse]
enabled = false
emit_message_text = false   # only message_hash by default for privacy
```

## Today

Sillok writes rows to `.sillok/telemetry.jsonl` regardless. To preview
the OTel translation today (without sending to Langfuse), use:

```bash
sillok sagwan tail --json | jq '.'
```

When the bridge ships, the same rows will be mirrored as OTLP spans.

## Privacy

Sillok stores `message_hash` (sha256 prefix) by default, **not** the
plaintext message. The Langfuse bridge inherits that default; setting
`emit_message_text = true` in the bridge config explicitly opts into
sending plaintext.

## Non-goals

- Langfuse self-hosting — operate Langfuse however you prefer.
- Replacing the local JSONL log — the bridge is additive; the local
  log remains the source of truth for replay (Top 10 Feature #10).
