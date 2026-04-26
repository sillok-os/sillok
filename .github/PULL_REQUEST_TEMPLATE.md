## What

<short user-visible summary>

## Why

Linked issue / roadmap item: <#... or F0.x / PR-A~K>

## How

Design notes. Link to ADR if this is an architectural change.

## Test evidence

```
# pytest output
```

For prompt or pack changes, include eval delta (when F0.7 is wired):

```
sillok gwageo run --suite all --baseline last
```

## Scope discipline checklist

- [ ] DCO sign-off on all commits (`git commit -s`)
- [ ] No silent system-prompt changes (proposals routed through Sangso)
- [ ] No vendor lock-in introduced
- [ ] Vault-resident corpus rule preserved (no system-global / `.sillok/`-isolated paths)
- [ ] Docs updated (README / ADR / module README) where applicable
- [ ] Tests added or updated
