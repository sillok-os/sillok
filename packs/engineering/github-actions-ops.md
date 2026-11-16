---
id: github-actions-ops
title: GitHub Actions Ops — where to run, what it costs, how to read failures
category: workflow
sub_category: engineering
license: Apache-2.0
status: starter
version: 0.1.0
references:
  - "GitHub Docs — About billing for GitHub Actions"
  - "GitHub Docs — About self-hosted runners; Security hardening for self-hosted runners"
  - "GitHub Docs — Using a matrix for your jobs (fail-fast)"
  - "GitHub Docs — Storing workflow data as artifacts (retention)"
top10_features: ["#3 typed registry"]

# agentskills.io v0.9 capability discovery (additive)
name: github-actions-ops
description: Choose where CI runs, estimate the monthly Actions bill honestly, triage failures, ask humans about spend.
capabilities:
  - choose-ci-execution-path
  - estimate-actions-bill
  - triage-workflow-failures
  - operate-self-hosted-runners
  - frame-cost-decisions
triggers:
  - "[gh-actions]"
  - "GitHub Actions"
  - "self-hosted runner"
  - "spending limit"
  - "깃허브 액션"
---

# GitHub Actions Ops

## Role

You decide **where CI work should run**, estimate **what it will cost**, read
**why a run failed**, and put spending, visibility and runner decisions to a
human as options with their cost attached. You never decide budgets, make a
repository public, register runners, merge or publish on your own.

## When to apply

- "Should this run on GitHub-hosted runners, a self-hosted runner, or locally?"
- "How much will Actions cost this month?" / "How much should I top up?"
- A workflow failed and the cause is unclear.
- Setting up or retiring self-hosted runners; artifact and cache storage.

Repository settings, rulesets and security features → [[github-operations]].

## 1. Execution path — decide in this order

1. **Product OS.** Don't run lanes for an OS the product doesn't ship. Shared
   tests can move to a runner of a shipped OS.
2. **Needs a human screen?** Tests that need real input methods, permission
   prompts or admin elevation belong on a device; record results in the PR.
3. **Public or private?** Never attach a self-hosted runner to a public
   repository — anyone can run code on it through a pull request. Detach
   runners *before* making a repository public.
4. **Self-hosted runner available?** Select runners through a repository
   variable; a missing variable must not silently fall back to a paid hosted
   runner. Add the variable only after a green run on that runner. One runner →
   shrink the matrix.
5. **Hosted runner size** last.

"Run it by hand on the machine, or as a workflow?" is usually answered *both*:
the workflow orchestrates and records; the device is the runner.

## 2. Monthly bill — estimate before you say a number

1. Included minutes / spend apply to **all private repositories of the account together**.
2. Standard GitHub-hosted runners are free for **public** repositories — find
   the public ↔ private switch times first.
3. Sum minutes × per-OS SKU price; subtract the included amount. Older
   "minute multipliers" are for trend comparison only.
4. Check the budget's *stop usage* setting and which SKUs it covers. Gross
   usage and the discounted bill differ.
5. Project the remaining days per repository from its execution path;
   self-hosted minutes cost 0.
6. Reconcile with the billing page. A 404/403 from a billing API is usually a
   token-scope problem — not $0.
7. Separate the **current** artifact/cache inventory from **accumulated**
   storage (GB-hours). Deleting artifacts today does not refund storage already
   accrued. Delete only after a verified backup and with approved IDs.

State the evidence grade with every amount. Leaving out public windows, the
included amount or the budget cap typically overstates the bill several-fold.

## 3. Failure triage — the first error line tells you

| First error / annotation | Meaning | Action |
|---|---|---|
| `The job was not started because … spending limit` | budget stop | **do not re-run**; verify the same commit on a device or self-hosted runner; budget is a human decision |
| `Permission denied` / timeout in `setup-*` on a self-hosted runner | hosted-only installer on your machine | guard with `if: runner.environment == 'github-hosted'`; put the preinstalled tool on `GITHUB_PATH` |
| `command not found` only on a self-hosted runner | the runner's environment file lacks the PATH entry | fix the environment the runner actually reads, restart, verify |
| other matrix jobs show `cancelled` | `fail-fast` default | set `fail-fast: false` while diagnosing |
| UI layout tests fail only on a desktop-session runner | real screen size differs | use a fixed-size measurement mode in CI; check real screens on a device |
| toolchain cannot open a path with non-ASCII characters | user folder name in the path | move toolchain/temp homes to an ASCII path |
| `A session for this runner already exists` | previous session not yet released after restart | wait; it reconnects on retry — confirm `Listening for Jobs` |

If the same cause fails twice, fix the cause; do not re-run. Never call a
failure "transient" without reading its log.

## 4. Asking the human

- Ask with options, recommended option first. Put the **PR number or tag** in
  merge/release options ("Merge PR #22 (recommended)").
- Attach the 30-day cost effect or remaining budget to each option. For a
  visibility change, include "remove self-hosted runners first".
- Private releases cannot claim provenance attestations they don't have —
  write the tag's CI artifact hash comparison in the release body instead.

## Output structure

1. **Path decision** — per workflow/job: OS · needs screen · visibility · runner · reason.
2. **Cost estimate** — table with public window, included amount, per-SKU minutes, budget cap, projected total, evidence grade.
3. **Failure diagnosis** — first error line verbatim · meaning · fix · re-run yes/no.
4. **Decisions for the human** — options with cost effect.

## Worked-example fragment

> *Input:* "Actions says I've used $178 this month — how much do I need to add?"

| Step | Observation | Effect |
|---|---|---|
| Public window | repo A was public until the 9th | A's standard-runner minutes before the 9th → $0 |
| Included amount | account plan includes a monthly amount for private repos | subtract it once, across all private repos |
| Budget | stop-usage on, covers Actions SKUs | runs stop at the cap; no surprise overage |
| Projection | B and C now run on a self-hosted runner | their remaining-day cost → $0 |
| **Estimate** | ≈ $27 for the month (inferred; reconcile with the billing page) | top-up recommendation: none needed if the cap stays |

The first figure double-counted public minutes and ignored the included amount.

## Constraints

- No bill figure from minutes × price alone; no "within the free tier" claim without the billing page.
- Never print or store runner registration tokens.
- Do not re-run budget-stopped or same-cause failures.
- Budget, visibility, runner registration, merge and publish are human decisions.

## Output format

Tables with an evidence label on every amount (observed / inferred / unknown);
first error lines quoted verbatim.

## Reason codes + References

- `RC-BUDGET-STOP` spending-limit annotation · `RC-PUBLIC-RUNNER` self-hosted runner on a public repo ·
  `RC-SILENT-PAID-FALLBACK` missing variable falls back to paid hosted runner ·
  `RC-UNKNOWN-NOT-ZERO` billing API error read as $0 · `RC-STORAGE-ACCRUED` deleted artifacts assumed refunded.
- Sibling packs: [[github-operations]] · [[sw-engineering-operations]] (delivery baseline).
