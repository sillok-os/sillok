# Proposal-Only Governance — `sillok.sangso`

> **Status**: shipped in v0.2.0a1 · Issue [#5](https://github.com/sillok-os/sillok/issues/5)
> **Module**: `sillok.sangso`
> **CLI**: `python -m sillok.sangso`

## Why

Sillok's repo description and Top 10 Feature #4 declare "proposal-only governance — hard guard against prompt drift and corpus poisoning." That promise demands two properties:

1. **No silent overwrites** — auto-growth from `sillok.eval` and telemetry never touches pack bodies directly.
2. **No machine-only approval path** — the human review step cannot be programmatically bypassed.

`sangso` (상소, "petition / formal proposal") implements both. Every change to a pack body, registry entry, or governance artifact lands first as a **proposal artifact** in `proposals/<id>.md`, runs through 4 gates, and waits for an interactive TTY confirmation before applying.

## The 4 gates

```
┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│  Gate 1     │   │  Gate 2     │   │  Gate 3     │   │  Gate 4     │
│  Lint       │ → │  Diff       │ → │  Eval Δ     │ → │  Approval   │
│  (schema)   │   │  (3-way)    │   │  (probes)   │   │  (artifact) │
└─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘
```

### Gate 1 — Lint

`gate_lint(proposed_text)` checks:

- Frontmatter parses as YAML
- Required fields present: `id`, `title`, `category`, `sub_category`, `version`, `license`
- Body length ≥ 200 lines (matches the bar set by Issue #1 acceptance)
- No broken markdown links (heuristic — empty-URL `[text]()` patterns)

### Gate 2 — Diff

`gate_diff(current_text, proposed_text)` is *informational* — it does not block. Output:

- Unified diff with 2-line context
- Added / removed line counts
- Section-level structural change summary (added / removed / kept)

The diff is included in the proposal artifact for human review.

### Gate 3 — Eval delta

`gate_eval_delta(pack_id, proposed_text, repo_root)`:

- Loads current registry via `sillok.naru.router_2tier.load_registry`
- Runs `sillok.eval.run_probes()` against the **baseline** registry → `pass_rate_baseline`
- Writes the proposed body to a tempfile, patches a tempfile registry pointing at it, runs probes again → `pass_rate_proposed`
- **Pass condition**: `pass_rate_proposed - pass_rate_baseline ≥ -5pp` (small regressions allowed for non-routing changes; large drops fail)

When `sillok.eval` is not installed (e.g., editable install without dev extras), the gate **gracefully skips** (passed=True, summary="skipped"). This keeps `sangso` usable in slim environments.

### Gate 4 — Approval artifact

`gate_approval_artifact(pack_id, diff_source, gates, proposals_dir)`:

- Synthesizes a `Proposal` dataclass with all gate results
- Writes `proposals/<YYYYMMDDTHHMMSSZ>-<pack_id>.md`
- Returns the artifact path

The artifact contains:

- Frontmatter: `proposal_id`, `pack_id`, `timestamp`, `diff_source`, `upstream_gates_passed`, `gate_count`
- Gate-results table
- Per-gate detail (YAML-serialized)
- Unified diff (separate fenced block)
- "How to apply" instructions

## CLI

```bash
# Run gates 1-4 against a proposed pack body
python -m sillok.sangso propose pm-enhanced --diff /tmp/new-pm-body.md

# List all proposals
python -m sillok.sangso list

# Render one proposal to stdout
python -m sillok.sangso show 20260509T120000Z-pm-enhanced

# Apply — REQUIRES INTERACTIVE TTY
python -m sillok.sangso accept 20260509T120000Z-pm-enhanced
# > About to overwrite:  packs/methodology/pm-enhanced.md
# > With contents from:  /tmp/new-pm-body.md
# > Type 'apply' (lowercase, no quotes) to proceed:
```

## Hard guards (the design intent)

By construction, the following are **impossible**:

| Guarded action | Mechanism |
|---|---|
| `--force` / `--yes` / `-y` / `--no-confirm` flag on `accept` | None defined; covered by `tests/unit/sangso/test_gates.py::test_no_force_flag_in_accept_command` |
| Auto-merge from non-TTY context | `accept` calls `sys.stdin.isatty()` and refuses without a TTY |
| Confirmation by hitting Enter | Must literally type `apply` — any other input aborts |
| Bypass when upstream gates failed | `accept` reads the artifact's frontmatter and refuses if `upstream_gates_passed: false` |

If you need to land a change that fails a gate (e.g., shipping a pack body shorter than 200 lines), the only paths are:

1. Fix the change so the gate passes
2. Edit the pack body **manually** outside the `sangso` flow (which records intent in git rather than in the proposal log)

This is intentional. Governance is a feature, not a roadblock.

## Future expansion (out of scope for v0.2.0a1)

- **Multi-reviewer workflow** — currently single-approver only
- **Web UI for proposal review** — CLI-first
- **Auto-rollback** — separate concern (v0.3.0)
- **Cryptographic signing of proposals** — provenance gate (P2)

## Module layout

```
sillok/sangso/
├── __init__.py        # public API exports
├── __main__.py        # click CLI: propose / list / show / accept
├── gates.py           # GateResult + 4 gate functions + run_all_gates
└── proposal.py        # Proposal dataclass + Markdown serialization

proposals/             # artifact storage (gitignored except .gitkeep)
└── .gitkeep
```

Tests: `tests/unit/sangso/test_gates.py` (10+ tests covering each gate + auto-merge guard).
