"""sillok.eval.evidence — execution-evidence records: what was *observed*, per stage.

Kernel (verification manager, ``gwageo``) · experimental since 0.4.0.

Agents report "installed", "working", "released" for things they only
inferred. This module validates a *supplied* evidence record so that a claim
is accepted only when every stage it depends on has an ``observed`` pass:

    release_verified  requires  placement + runtime_identity + activation
                                + functional + real_use   (all observed, all
                                bound to the same artifact sha256)

and a batch record reconciles a frozen set of item IDs against per-item stage
receipts, keeping *data complete* separate from *final complete* (cleanup
observed, nothing pending).

Scope: read-only consistency of the record you pass in. It never opens the
referenced evidence, runs commands, or checks OS/auth state — a passing
record proves the record is consistent, not that the observation happened.

CLI::

    python -m sillok.eval.evidence check record.json
    python -m sillok.eval.evidence check-batch closeout.json
    python -m sillok.eval.evidence contract            # contract ↔ code drift
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "execution-evidence-v1"
BATCH_SCHEMA_VERSION = "execution-batch-v1"
CONTRACT_PATH = Path(__file__).resolve().parent / "contracts" / "execution-evidence.json"

BATCH_KEYS = {
    "schema_version",
    "task_id",
    "attempt_id",
    "observed_at",
    "context",
    "scope",
    "expected_ids",
    "required_stages",
    "receipts",
    "cleanup",
    "pending",
    "data_complete",
    "final_complete",
}
STAGES = (
    "placement",
    "runtime_identity",
    "activation",
    "functional",
    "real_use",
    "browser_approval",
    "cli_auth",
    "inference",
    "remote_identity",
    "transfer_receipt",
    "network_request",
    "static_review",
)
STATUSES = ("pass", "fail", "unverified", "unavailable")
BASES = ("observed", "agent_reported", "user_reported", "inferred")
SURFACES = (
    "browser",
    "claude",
    "codex",
    "user_terminal",
    "remote_desktop",
    "external_agent",
    "ci",
)
ACTORS = ("agent", "user", "unknown")
CLAIM_REQUIREMENTS: dict[str, tuple[str, ...]] = {
    "installation_verified": ("placement",),
    "runtime_verified": ("runtime_identity",),
    "release_verified": ("placement", "runtime_identity", "activation", "functional", "real_use"),
    "cli_authenticated": ("cli_auth",),
    "cli_usable": ("cli_auth", "inference"),
    "remote_execution_verified": ("remote_identity",),
    "transfer_verified": ("transfer_receipt",),
    "static_review_completed": ("static_review",),
}
#: Stages whose pass must be bound to the artifact hash (same build, not a rebuild).
BINARY_STAGES = {"placement", "runtime_identity", "activation", "functional", "real_use"}

_SHA = re.compile(r"^[0-9a-f]{64}$")
_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:@/-]{0,199}$")
#: Evidence references must never carry credentials.
_SECRET = re.compile(
    r"(?i)bearer\s|(?:token|password|secret|authorization|auth[-_]code)\s*[:=]|"
    r"\b[A-Z0-9]{4,5}-[A-Z0-9]{4,5}\b|[A-Za-z0-9_-]{20,}#[A-Za-z0-9_-]{10,}|"
    r"\b(?:sk-|sk-ant-|ghp_|github_pat_)[A-Za-z0-9_-]+"
)


def _object(
    value: Any, allowed: set[str], required: set[str], label: str, errors: list[str]
) -> bool:
    if not isinstance(value, dict):
        errors.append(label + ":object_required")
        return False
    if set(value) - allowed:
        errors.append(label + ":unknown_fields")
    if required - set(value):
        errors.append(label + ":missing_fields")
    return True


def _text(value: Any, *, limit: int = 2000) -> bool:
    """Short, printable, secret-free text without query strings."""
    return (
        isinstance(value, str)
        and 0 < len(value) <= limit
        and not _SECRET.search(value)
        and "?" not in value
        and not any(ord(c) < 32 for c in value)
    )


def check_record(doc: Any, *, surfaces: tuple[str, ...] = SURFACES) -> dict[str, Any]:
    """Validate one record. Errors name fields, never echo input values."""
    errors: list[str] = []
    root_keys = {
        "schema_version",
        "task_id",
        "attempt_id",
        "observed_at",
        "context",
        "artifact",
        "checks",
        "claims",
    }
    if not _object(doc, root_keys, root_keys - {"artifact"}, "record", errors):
        return _report(errors, [])
    if doc.get("schema_version") != SCHEMA_VERSION:
        errors.append("record:schema_version")
    for key in ("task_id", "attempt_id"):
        v = doc.get(key)
        if not _text(v, limit=200) or not _ID.fullmatch(v):
            errors.append(key + ":invalid_identifier")
    try:
        ts = datetime.fromisoformat(doc["observed_at"].replace("Z", "+00:00"))
        if ts.tzinfo is None or ts.utcoffset() is None:
            raise ValueError
    except (ValueError, TypeError, KeyError, AttributeError):
        errors.append("observed_at:timezone_required")

    ctx = doc.get("context")
    ctx_keys = {"source_host", "target_host", "surface", "permission", "actor"}
    if _object(ctx, ctx_keys, ctx_keys, "context", errors):
        for key in ctx_keys:
            if not _text(ctx.get(key), limit=200):
                errors.append("context:" + key + ":invalid")
        if ctx.get("actor") not in ACTORS:
            errors.append("context:actor:unknown")
        if ctx.get("surface") not in surfaces:
            errors.append("context:surface:unknown")

    artifact = doc.get("artifact")
    artifact_hash = None
    if "artifact" in doc and _object(
        artifact, {"ref", "sha256", "commit"}, {"ref", "sha256"}, "artifact", errors
    ):
        if not _text(artifact.get("ref")):
            errors.append("artifact:ref:invalid")
        artifact_hash = artifact.get("sha256")
        if not isinstance(artifact_hash, str) or not _SHA.fullmatch(artifact_hash):
            errors.append("artifact:sha256:invalid")
        commit = artifact.get("commit")
        if "commit" in artifact and (
            not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{7,64}", commit)
        ):
            errors.append("artifact:commit:invalid")

    checks = doc.get("checks")
    by_stage: dict[str, dict[str, Any]] = {}
    if not isinstance(checks, list) or len(checks) > 50:
        errors.append("checks:array_required_or_too_large")
        checks = []
    for i, check in enumerate(checks):
        label = f"checks[{i}]"
        if not _object(
            check,
            {"stage", "status", "basis", "evidence", "subject_sha256"},
            {"stage", "status", "basis", "evidence"},
            label,
            errors,
        ):
            continue
        stage = check.get("stage")
        if not isinstance(stage, str) or stage not in STAGES:
            errors.append(label + ":unknown_stage")
            continue
        if stage in by_stage:
            errors.append(label + ":duplicate_stage")
        by_stage[stage] = check
        if check.get("status") not in STATUSES:
            errors.append(label + ":unknown_status")
        if check.get("basis") not in BASES:
            errors.append(label + ":unknown_basis")
        refs = check.get("evidence")
        if not isinstance(refs, list) or len(refs) > 30 or not all(_text(r) for r in refs):
            errors.append(label + ":invalid_evidence_refs")
        elif check.get("status") in ("pass", "fail") and not refs:
            errors.append(label + ":evidence_required")
        subject = check.get("subject_sha256")
        if "subject_sha256" in check and (
            not isinstance(subject, str) or not _SHA.fullmatch(subject)
        ):
            errors.append(label + ":invalid_subject_sha256")

    claims = doc.get("claims")
    if not isinstance(claims, list) or len(claims) > len(CLAIM_REQUIREMENTS):
        errors.append("claims:array_required_or_too_large")
        claims = []
    verified: list[str] = []
    for claim in claims:
        if not isinstance(claim, str) or claim not in CLAIM_REQUIREMENTS:
            errors.append("claims:unknown_claim")
            continue
        if claim in verified:
            errors.append("claims:duplicate_claim")
        before = len(errors)
        for stage in CLAIM_REQUIREMENTS[claim]:
            c = by_stage.get(stage)
            if not c or c.get("status") != "pass" or c.get("basis") != "observed":
                errors.append(claim + ":requires_observed_pass:" + stage)
            elif stage in BINARY_STAGES and (
                not artifact_hash or c.get("subject_sha256") != artifact_hash
            ):
                errors.append(claim + ":artifact_binding_required:" + stage)
        if len(errors) == before:
            verified.append(claim)
    return _report(errors, verified)


def _report(errors: list[str], verified: list[str]) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "valid": not errors,
        "verified_claims": [] if errors else verified,
        "errors": errors,
        "verification_scope": "supplied-record-consistency-only",
        "executed_actions": False,
    }


def check_batch(doc: Any, *, surfaces: tuple[str, ...] = SURFACES) -> dict[str, Any]:
    """Reconcile a frozen item set; data success never implies cleanup success.

    A count match is not completion — the *set* of item IDs that passed each
    required stage must equal ``expected_ids``. ``final_complete`` further
    requires an observed cleanup (or an observed "not required") and an empty
    ``pending`` list.
    """
    errors: list[str] = []
    result: dict[str, Any] = {
        "schema_version": BATCH_SCHEMA_VERSION,
        "valid": False,
        "expected_count": 0,
        "stage_counts": {},
        "data_complete": False,
        "final_complete": False,
        "errors": errors,
        "verification_scope": "supplied-record-consistency-only",
        "executed_actions": False,
    }
    if not _object(doc, BATCH_KEYS, BATCH_KEYS, "batch", errors):
        return result
    if doc.get("schema_version") != BATCH_SCHEMA_VERSION:
        errors.append("batch:schema_version")
    meta = {k: doc.get(k) for k in ("task_id", "attempt_id", "observed_at", "context")}
    meta.update(schema_version=SCHEMA_VERSION, artifact=doc.get("scope"), checks=[], claims=[])
    errors.extend(check_record(meta, surfaces=surfaces)["errors"])

    def identifiers(value: Any, label: str, limit: int) -> list[str]:
        if (
            not isinstance(value, list)
            or not 1 <= len(value) <= limit
            or not all(_text(v, limit=200) and _ID.fullmatch(v) for v in value)
        ):
            errors.append(label + ":invalid_identifiers")
            return []
        if len(set(value)) != len(value):
            errors.append(label + ":duplicates")
        return list(dict.fromkeys(value))

    def observation(value: dict[str, Any], label: str, *, not_required: bool = False) -> bool:
        statuses = STATUSES + (("not_required",) if not_required else ())
        if value.get("status") not in statuses:
            errors.append(label + ":unknown_status")
        if value.get("basis") not in BASES:
            errors.append(label + ":unknown_basis")
        refs = value.get("evidence")
        if not isinstance(refs, list) or len(refs) > 30 or not all(_text(r) for r in refs):
            errors.append(label + ":invalid_evidence_refs")
            return False
        if value.get("status") in ("pass", "fail", "not_required") and not refs:
            errors.append(label + ":evidence_required")
        return bool(refs) and value.get("status") == "pass" and value.get("basis") == "observed"

    expected = set(identifiers(doc.get("expected_ids"), "expected_ids", 10000))
    stages = identifiers(doc.get("required_stages"), "required_stages", 50)
    passed: dict[str, set[str]] = {stage: set() for stage in stages}
    seen: set[tuple[str, str]] = set()
    receipts = doc.get("receipts")
    if not isinstance(receipts, list) or len(receipts) > 500000:
        errors.append("receipts:array_required_or_too_large")
        receipts = []
    for i, receipt in enumerate(receipts):
        label = f"receipts[{i}]"
        keys = {"id", "stage", "status", "basis", "evidence"}
        if not _object(receipt, keys, keys, label, errors):
            continue
        item, stage = receipt.get("id"), receipt.get("stage")
        observed = observation(receipt, label)
        if not isinstance(item, str) or item not in expected:
            errors.append(label + ":outside_frozen_scope")
            continue
        if not isinstance(stage, str) or stage not in passed:
            errors.append(label + ":unknown_stage")
            continue
        if (item, stage) in seen:
            errors.append(label + ":duplicate_item_stage")
        seen.add((item, stage))
        if observed:
            passed[stage].add(item)

    cleanup = doc.get("cleanup")
    cleanup_done = False
    keys = {"required", "status", "basis", "evidence"}
    if _object(cleanup, keys, keys, "cleanup", errors):
        observed = observation(cleanup, "cleanup", not_required=True)
        if type(cleanup.get("required")) is not bool:
            errors.append("cleanup:required_boolean")
        elif cleanup["required"]:
            if cleanup.get("status") == "not_required":
                errors.append("cleanup:required_but_not_required")
            cleanup_done = observed
        else:
            if cleanup.get("status") != "not_required":
                errors.append("cleanup:explicit_not_required_expected")
            cleanup_done = (
                cleanup.get("status") == "not_required"
                and cleanup.get("basis") == "observed"
                and bool(cleanup.get("evidence"))
            )
    pending = doc.get("pending")
    if not isinstance(pending, list) or len(pending) > 100 or not all(_text(p) for p in pending):
        errors.append("pending:invalid_array")
    for key in ("data_complete", "final_complete"):
        if type(doc.get(key)) is not bool:
            errors.append(key + ":boolean_required")
    data_done = bool(expected and stages) and all(ids == expected for ids in passed.values())
    final_done = data_done and cleanup_done and pending == []
    if doc.get("data_complete") is True and not data_done:
        errors.append("data_complete:incomplete_item_stages")
    if doc.get("final_complete") is True and (
        doc.get("data_complete") is not True or not final_done
    ):
        errors.append("final_complete:requires_data_cleanup_and_no_pending")
    result.update(
        valid=not errors,
        expected_count=len(expected),
        stage_counts={stage: len(ids) for stage, ids in passed.items()},
        data_complete=data_done and not errors,
        final_complete=final_done and doc.get("final_complete") is True and not errors,
    )
    return result


def contract_consistency(path: Path = CONTRACT_PATH) -> dict[str, Any]:
    """Detect drift between the JSON contract and the rules embedded here.

    The JSON is the published contract; runtime judgement uses the constants
    in this module. When they disagree, ``valid`` is False — a human fixes
    one side (no automatic sync).
    """
    errors: list[str] = []
    try:
        contract = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeError):
        return {
            "valid": False,
            "contract": str(path),
            "errors": ["contract:unreadable_or_invalid_json"],
        }
    if not str(contract.get("$id", "")).endswith(SCHEMA_VERSION):
        errors.append("contract:$id_version_mismatch")
    required = set(contract.get("required") or [])
    if required != {
        "schema_version",
        "task_id",
        "attempt_id",
        "observed_at",
        "context",
        "checks",
        "claims",
    }:
        errors.append("contract:required_root_keys_mismatch")
    claims = contract.get("x-sillok-claim-requirements") or {}
    if {k: list(v) for k, v in claims.items()} != {
        k: list(v) for k, v in CLAIM_REQUIREMENTS.items()
    }:
        errors.append("contract:claim_requirements_mismatch")
    if "sillok.eval.evidence check" not in str(contract.get("x-sillok-semantic-validator", "")):
        errors.append("contract:semantic_validator_not_this_module")
    surface_enum = (
        ((contract.get("properties") or {}).get("context") or {})
        .get("properties", {})
        .get("surface", {})
    )
    if set(surface_enum.get("enum") or []) != set(SURFACES):
        errors.append("contract:surface_enum_mismatch")
    check_props = ((contract.get("$defs") or {}).get("check") or {}).get("properties") or {}
    for field, allowed in (("stage", STAGES), ("status", STATUSES), ("basis", BASES)):
        enum = (check_props.get(field) or {}).get("enum")
        if enum is not None and set(enum) != set(allowed):
            errors.append(f"contract:{field}_enum_mismatch")
    batch = (contract.get("$defs") or {}).get("batch", {})
    if (
        set(batch.get("required", [])) != BATCH_KEYS
        or set(batch.get("properties", {})) != BATCH_KEYS
    ):
        errors.append("contract:batch_keys_mismatch")
    if batch.get("properties", {}).get("schema_version", {}).get("const") != BATCH_SCHEMA_VERSION:
        errors.append("contract:batch_version_mismatch")
    if "sillok.eval.evidence check-batch" not in str(contract.get("x-sillok-batch-validator", "")):
        errors.append("contract:batch_validator_mismatch")
    return {
        "valid": not errors,
        "contract": str(path),
        "schema_version": SCHEMA_VERSION,
        "errors": errors,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m sillok.eval.evidence", description=__doc__)
    ap.add_argument("command", choices=["check", "check-batch", "contract"])
    ap.add_argument("file", type=Path, nargs="?")
    args = ap.parse_args(argv)
    if args.command == "contract":
        result = contract_consistency(args.file or CONTRACT_PATH)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["valid"] else 1
    if args.file is None:
        ap.error(f"{args.command} needs <record.json>")
    try:
        doc = json.loads(args.file.read_text(encoding="utf-8"))
        result = check_batch(doc) if args.command == "check-batch" else check_record(doc)
    except (OSError, ValueError, UnicodeError):
        result = _report(["input:unreadable_or_invalid_json"], [])
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
