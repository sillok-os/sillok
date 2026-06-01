# SPDX-License-Identifier: Apache-2.0
"""sillok.telemetry.gate — schema-enforced telemetry write-gate.

Every telemetry row is validated against the canonical
``sillok.schemas.telemetry`` schema **before** it is appended to the jsonl log.
A single malformed row silently poisons the corpus that ``sillok.eval`` (Gwageo)
and the self-improvement loop read — so the gate catches it at write time,
where the error is cheap.

This is a distinct concern from :mod:`sillok.sangso.gates` (the 4-gate proposal
governance over pack/registry changes). The telemetry gate governs *data writes*.

Provider-neutral: no LLM/IDE/DB dependency. Degrades gracefully when Pydantic
is absent (``HAS_PYDANTIC is False``) to a minimal required-field check.

Usage (CLI)::

    python -m sillok.telemetry.gate --validate path/to/telemetry.jsonl
    python -m sillok.telemetry.gate --validate path/to/telemetry.jsonl --schema v2

Usage (programmatic)::

    from pathlib import Path
    from sillok.telemetry.gate import write_v2

    write_v2(record, Path("telemetry.jsonl"))  # returns True iff appended
"""

from __future__ import annotations

import argparse
import contextlib
import json
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

from sillok.schemas import HAS_PYDANTIC, LegacyTelemetryRow, TelemetryRow

# Canonical required-field sets, used only on the no-pydantic fallback path.
_V2_REQUIRED = ("trace_id", "timestamp", "input", "output", "metadata", "scores")
_LEGACY_REQUIRED = (
    "timestamp",
    "message",
    "selected_pack_ids",
    "selected_categories",
    "confidence",
    "applied_prompt_packs_line",
)

# Optional observability extension point. A downstream may assign a callable
# ``(record: dict) -> None`` that runs after validation, before append. It must
# never block the write: any exception it raises is swallowed (warning-only).
divergence_hook: Callable[[dict[str, Any]], None] | None = None


def _run_hook(record: dict[str, Any]) -> None:
    if divergence_hook is None:
        return
    # observability must never break the write path
    with contextlib.suppress(Exception):
        divergence_hook(record)


def validate_v2(record: dict[str, Any]) -> tuple[bool, str | None]:
    """Validate ``record`` against the v2 ``TelemetryRow`` schema.

    Returns ``(ok, error_message_or_None)``.
    """
    if not HAS_PYDANTIC:
        missing = set(_V2_REQUIRED) - set(record.keys())
        if missing:
            return False, f"missing fields (no-pydantic mode): {sorted(missing)}"
        return True, None
    try:
        TelemetryRow.model_validate(record)
        return True, None
    except Exception as exc:  # pydantic ValidationError or coercion failure
        return False, str(exc)


def validate_legacy(record: dict[str, Any]) -> tuple[bool, str | None]:
    """Validate ``record`` against the legacy schema (read-compat window)."""
    if not HAS_PYDANTIC:
        missing = set(_LEGACY_REQUIRED) - set(record.keys())
        if missing:
            return False, f"missing fields (no-pydantic mode): {sorted(missing)}"
        return True, None
    try:
        LegacyTelemetryRow.model_validate(record)
        return True, None
    except Exception as exc:
        return False, str(exc)


def _append(record: dict[str, Any], dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")


def write_v2(record: dict[str, Any], dest: Path) -> bool:
    """Validate then append a v2 record. Returns ``True`` iff appended."""
    ok, err = validate_v2(record)
    if not ok:
        print(f"telemetry-gate: v2 validation failed -> {err}", file=sys.stderr)
        return False
    _run_hook(record)
    _append(record, dest)
    return True


def write_legacy(record: dict[str, Any], dest: Path) -> bool:
    """Validate then append a legacy record. Returns ``True`` iff appended."""
    ok, err = validate_legacy(record)
    if not ok:
        print(f"telemetry-gate: legacy validation failed -> {err}", file=sys.stderr)
        return False
    _run_hook(record)
    _append(record, dest)
    return True


def cli_validate(path: Path, schema: str = "auto") -> int:
    """Validate every line of a jsonl file. Returns a process exit code."""
    if not path.exists():
        print(f"file not found: {path}", file=sys.stderr)
        return 1
    total = passed = 0
    failures: list[dict[str, Any]] = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        total += 1
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            failures.append({"line": lineno, "error": f"JSONDecodeError: {exc}"})
            continue
        target = schema
        if schema == "auto":
            target = "v2" if "trace_id" in record else "legacy"
        ok, err = validate_v2(record) if target == "v2" else validate_legacy(record)
        if ok:
            passed += 1
        else:
            failures.append({"line": lineno, "schema": target, "error": err})

    print(f"telemetry-gate validate: {passed}/{total} records passed")
    for failure in failures[:5]:
        print(f"  L{failure['line']} [{failure.get('schema', '?')}] {failure['error']}")
    return 0 if passed == total else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="sillok.telemetry.gate",
        description="Schema-enforced telemetry write-gate.",
    )
    parser.add_argument(
        "--validate",
        type=Path,
        metavar="JSONL_PATH",
        help="validate every line in a jsonl file",
    )
    parser.add_argument("--schema", choices=["auto", "v2", "legacy"], default="auto")
    args = parser.parse_args(argv)
    if args.validate:
        return cli_validate(args.validate, schema=args.schema)
    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
