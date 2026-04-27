# Contributing to Sillok

Thank you for considering a contribution. Sillok runs on a **proposal-only governance model** (Top 10 Feature #4) — the same discipline applies to contributions to the project itself.

## TL;DR

1. **Sign your commits with DCO** — every commit must carry a `Signed-off-by:` trailer (`git commit -s`).
2. **Open an issue or discussion first** for non-trivial changes — saves wasted work if the direction does not fit the roadmap.
3. **Tests + eval probes must pass** — `pytest` + `sillok gwageo run --suite all` (when implemented in F0.7).
4. **Code style** — `ruff format` + `ruff check` + `mypy --strict`.
5. **Follow the Conventional Commit format** — `<type>(<scope>): <summary>` (e.g., `feat(naru): add tier-2 LLM intent fallback`).

## Developer Certificate of Origin (DCO)

Sillok requires DCO sign-off in lieu of a CLA. By adding `Signed-off-by:` to your commit, you certify that you wrote (or have rights to submit) the code under the project's license. See <https://developercertificate.org/> for the full text.

```bash
git commit -s -m "feat(bongsu): add dual_compare retrieval plan"
```

## Workflow

1. Fork `sillok-os/sillok` and create a topic branch.
2. Implement your change with tests.
3. Run the local checks:
   ```bash
   ruff format
   ruff check
   mypy sillok/
   pytest
   # When eval is wired (F0.7+):
   sillok gwageo run --suite all --baseline last
   ```
4. Open a pull request to `main`. Include in the PR description:
   - **What** — the user-visible change
   - **Why** — the motivating issue or roadmap item
   - **How** — design notes (link to ADR if needed)
   - **Test evidence** — pytest output + eval delta
5. CI must be green. Maintainers will review against the [governance gates](GOVERNANCE.md).

## Scope discipline

- **No silent system-prompt changes.** Pack body or registry changes go through `sillok sangso` proposal — even when proposed by a maintainer.
- **No vendor lock-in.** Sillok must remain provider-neutral. PRs adding hard dependencies on a single LLM/IDE/DB are unlikely to be accepted.
- **vault-resident corpus only.** PRs reintroducing system-global or `.sillok/`-isolated corpus paths will be rejected. See K-6 ablation in the README.
- **Top 10 Features are load-bearing.** Removing or weakening any of the 10 features requires an ADR.

## Adding a pack for your domain / industry

If you're contributing a new pack covering an industry (Banking, Insurance, Automotive, Medical Device, Embedded, …), a methodology family (NIST RMF, FAIR, Change Management, Org Design, …), or a specialty practice (M&A diligence, Pricing, GTM, Growth, UX research, …), follow the dedicated guide:

→ [`docs/contributing/extending-with-your-domain.md`](docs/contributing/extending-with-your-domain.md)

It covers pack anatomy, registry entry, sanitization checklist (the most common reason a PR gets sent back), standards-citation rule (nominative fair use), framework-coverage inventory update, the 5-step quality gate, and the PR workflow for external contributors and maintainer SMEs.

The 17–18 of the 25 categories that are not yet shipped in the alpha are intentionally left for domain SMEs — your contribution lands additively.

## Issue triage

- `type:bug` → reproduction steps mandatory
- `type:feature` → must map to an existing roadmap item or add an ADR proposing one
- `type:docs` → small, isolated PRs are encouraged (typo, clarity)
- `type:question` → please use Discussions instead

## Releases

Versioning follows SemVer (see [`docs/governance/semver-policy.md`](docs/governance/semver-policy.md) when published). Maintainers cut releases; contributors do not push tags directly.

## Code of Conduct

By participating, you agree to abide by the project's [Code of Conduct](CODE_OF_CONDUCT.md) (Contributor Covenant 2.1).

## Questions?

- Discussions: <https://github.com/sillok-os/sillok/discussions>
- Security issues: see [`SECURITY.md`](SECURITY.md) — do **not** open public issues for security vulnerabilities.
