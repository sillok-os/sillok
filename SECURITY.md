# Security Policy

## Reporting

Please report suspected vulnerabilities **privately** via either:

- GitHub Security Advisories: <https://github.com/sillok-os/sillok/security/advisories/new>
- Email: <tykim21@gmail.com>

Do **not** open public issues for vulnerabilities until a fix is available.

## Response targets

| Stage | Target |
|---|---|
| Acknowledgement | within 3 business days |
| Triage + severity | within 7 business days |
| Fix or mitigation | depends on severity (Critical: 14 days target) |
| Public advisory | after fix is released or with reporter coordination |

## Scope

In scope: the `sillok` package and first-party `sillok-*` subpackages maintained under <https://github.com/sillok-os>.

Out of scope: third-party LLM providers, MCP clients, IDEs, or user-supplied vault content.

## Supported versions

Until v1.0.0 GA, only the latest minor pre-release (e.g., the most recent `0.X.Y`) receives fixes. Older pre-releases are not patched.
