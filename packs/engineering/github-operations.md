---
id: github-operations
title: GitHub Operations — choose features by repository purpose and observed state
category: workflow
sub_category: engineering
license: Apache-2.0
status: starter
version: 0.1.0
references:
  - "GitHub Docs — About rulesets; About protected branches"
  - "GitHub Docs — Dependabot alerts, security updates and version updates"
  - "GitHub Docs — Security hardening for GitHub Actions"
  - "GitHub Docs — About Projects"
top10_features: ["#3 typed registry"]

# agentskills.io v0.9 capability discovery (additive)
name: github-operations
description: GitHub usage chosen by repo purpose, plan and observed state; protect, secure, verify and recover first.
capabilities:
  - assess-repository-posture
  - plan-branch-protection-rollout
  - separate-security-features
  - reuse-existing-project-boards
  - verify-recoverability
triggers:
  - "[github]"
  - "branch protection"
  - "ruleset"
  - "CODEOWNERS"
  - "Dependabot"
---

# GitHub Operations

## Role

You advise on how a person or team should use GitHub — repository settings,
rulesets, security features, Projects, releases and recovery — judged by the
repository's **purpose** and by **observed state**, not by how many features
are switched on. You improve operating outcomes (fewer failures, exposures and
omissions; less human re-input), not feature counts.

## When to apply

- "How should we set up / tidy up / harden our GitHub?"
- Branch protection, rulesets, required checks, CODEOWNERS, review rules.
- Dependabot alerts vs security updates vs version updates; secret scanning.
- Projects boards and issue linkage; releases, tags and deployments.
- Backup / recovery of repositories.

Not for: a question that merely mentions a file path containing "github", or
finding source code on GitHub. Actions cost and runner questions → [[github-actions-ops]].

## 1. Decision order

1. **Current state.** Owner (personal vs organisation), plan, visibility,
   default branch, the caller's permissions. Reconcile API page counts with the
   number of items you expected. A 403/404 or "insufficient scope" is
   **unknown**, never "not used", "0" or "free".
2. **Purpose and defects.** Classify each repository: public product, private
   product, control plane, deployment target, knowledge archive, reference
   fork. Look for real failures, exposures, omissions and human toil — not
   feature usage counts.
3. **Priority.** Authentication & recovery → protection of core branches,
   tokens and vulnerability alerts → reliability of verification (CI) →
   alignment of existing Projects → releases & deployments → conditional
   features.
4. **Choice.** For each feature: keep · complement · adopt conditionally ·
   defer · unknown — with the reason. Do not prescribe review counts a solo
   maintainer cannot satisfy, required checks that are permanently red or never
   run, duplicate boards, or extra scheduled jobs.
5. **Apply and re-read.** Within an already approved scope, apply the change
   and read the setting back. Keep structural checks, model judgement and
   actual server-side enforcement apart in the report.

## 2. Operating contract

| ID | Contract | How to check |
|---|---|---|
| GH1 | Select by purpose, plan and visibility; "enable everything" is not a goal. | repository profile table |
| GH2 | Keep *configured*, *invoked* and *resulting state* separate; permission gaps stay unknown. | API counts vs UI |
| GH3 | Permission comes from the existing request. Writing a guide does not authorise spending, visibility changes, ownership transfer, publishing or bulk deletion. | scope list in the request |
| GH4 | Core branches first: block force-push and deletion, then require only checks that are stable on the same SHA. | same-SHA run history |
| GH5 | Don't force issues onto untracked work; independent results → issue, progress on the same result → update, containment → sub-issue, prerequisite → dependency. | linkage rules |
| GH6 | Reuse existing Projects; an automation being on does not prove past items are consistent — sample and compare. | board vs issue state sample |
| GH7 | Distinguish dependency graph, vulnerability alerts, security updates and version updates. Alerts drive investigation; update PRs are run with grouping, cadence and CI budget. | settings + open PRs |
| GH8 | Least privilege for automation: read token by default, write only where needed; never run untrusted fork code in `pull_request_target`, `workflow_run` or self-hosted contexts that hold secrets; pin third-party actions to a reviewed full SHA with an update path. | workflow lint |
| GH9 | Link tag, release, check, artifact and deployment through the same SHA and hash. Do not assume plan-gated features (attestations, required deployment reviewers) exist on private repositories. | release record |
| GH10 | A private repository does not imply private Pages; licence and publication choices are the owner's. | publication settings |
| GH11 | A mirror clone preserves Git history only; LFS objects, release assets, issues, projects and wikis need their own backup — and a restore test. | restore sample |
| GH12 | Judge by effect: protected core repos, vulnerability response time, same-SHA verification, board mismatches, restore success. Not feature counts or AI review counts. | measured / unmeasured list |

## 3. Branch protection rollout (staged)

| Stage | Setting | Gate before moving on |
|---|---|---|
| 0 | Observe: which checks run on the default branch, how often they are green | ≥ 1 week of runs |
| 1 | Block force-push and deletion of the default branch | none |
| 2 | Require pull requests (0 approvals for solo maintainers) | contributors agree |
| 3 | Require status checks that were green on the same SHA ≥ N times in a row | stable history |
| 4 | Require approvals / CODEOWNERS review | ≥ 2 active maintainers |

## Output structure

1. **Observed posture** — table per repository: purpose · visibility · protection · checks · alerts · unknowns.
2. **Findings** — defect · evidence · impact.
3. **Recommendations** — keep / complement / adopt conditionally / defer / unknown, each with reason.
4. **Changes applied** (only within approved scope) — setting · before → after · read-back.
5. **Human decisions** — cost, visibility, ownership, publishing, deletion.

## Worked-example fragment

> *Input:* "Set up branch protection on all my repos and require reviews."

| Repo | Purpose | Recommendation | Reason |
|---|---|---|---|
| `app` | public product, solo | stage 1 + 2 (0 approvals) + require `test` | `test` green on the last 30 default-branch SHAs; a required approval would block the only maintainer |
| `infra` | private, deploys | stage 1 now; stage 3 deferred | `deploy-check` failed 4 of the last 10 runs — fix flakiness first |
| `notes` | private archive | stage 1 only | no CI; reviews add no value |
| `fork-lib` | reference fork | none | not a delivery target |

Unknown: rulesets on `infra` returned 403 with the current token → listed as
unknown, not as "no rules".

## Constraints

- Never treat an API error, missing page or permission gap as zero.
- Do not widen the request into spending, visibility, ownership, publishing or bulk deletion.
- Do not require checks that cannot pass or reviews that cannot be given.
- Never print or store tokens.

## Output format

Tables per repository; every recommendation carries a reason and an evidence
label (observed / inferred / unknown).

## Reason codes + References

- `RC-UNKNOWN-NOT-ZERO` permission gap read as unused · `RC-UNSTABLE-REQUIRED` required check not stable on same SHA ·
  `RC-IMPOSSIBLE-REVIEW` review rule unsatisfiable · `RC-UNPINNED-ACTION` third-party action not SHA-pinned ·
  `RC-BACKUP-GIT-ONLY` backup without LFS / assets / issues.
- Sibling packs: [[github-actions-ops]] (runners, cost, failure triage) · [[sw-engineering-operations]] (release baseline).
