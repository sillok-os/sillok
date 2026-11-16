"""Execution-evidence regressions (ported from the upstream harness, 0.4.0).

Mined from real cases: an input-method release where "installed" was reported
as "running", an external CLI where browser consent was reported as CLI login,
and a long batch where a matching count hid a different item set.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from sillok.eval import evidence as ev
from sillok.eval.evidence import CONTRACT_PATH, check_record


def record(*stages, claims=()):
    return {
        "schema_version": "execution-evidence-v1",
        "task_id": "case-fixture",
        "attempt_id": "attempt-1",
        "observed_at": "2026-10-20T05:00:00+09:00",
        "context": {
            "source_host": "fixture-mac",
            "target_host": "fixture-vm",
            "surface": "browser",
            "permission": "guard",
            "actor": "agent",
        },
        "artifact": {"ref": "repo:fixture/binary", "sha256": "a" * 64},
        "checks": [
            {
                "stage": s,
                "status": "pass",
                "basis": "observed",
                "evidence": ["fixture:observation"],
                "subject_sha256": "a" * 64,
            }
            for s in stages
        ],
        "claims": list(claims),
    }


def test_file_install_does_not_imply_runtime():
    r = check_record(record("placement", claims=["runtime_verified"]))
    assert not r["valid"] and "runtime_identity" in str(r["errors"])


def test_browser_consent_does_not_imply_cli_login():
    assert not check_record(record("browser_approval", claims=["cli_authenticated"]))["valid"]


def test_release_requires_all_five_layers():
    stages = ["placement", "runtime_identity", "activation", "functional", "real_use"]
    assert check_record(record(*stages, claims=["release_verified"]))["valid"]
    for absent in stages:
        assert not check_record(
            record(*(s for s in stages if s != absent), claims=["release_verified"])
        )["valid"]


def test_reported_or_inferred_pass_is_not_direct_verification():
    for basis in ["agent_reported", "user_reported", "inferred"]:
        r = record("cli_auth", claims=["cli_authenticated"])
        r["checks"][0]["basis"] = basis
        assert not check_record(r)["valid"]


def test_observation_gap_is_preserved_without_claim():
    r = record("runtime_identity")
    r["checks"][0].update(status="unavailable", basis="agent_reported", evidence=[])
    assert check_record(r)["valid"]
    assert check_record(r)["verified_claims"] == []


def test_wrong_binary_hash_does_not_verify_runtime():
    r = record("runtime_identity", claims=["runtime_verified"])
    r["checks"][0]["subject_sha256"] = "b" * 64
    assert not check_record(r)["valid"]


def test_duplicate_stage_cannot_hide_failure():
    r = record("cli_auth", claims=["cli_authenticated"])
    r["checks"].append({**r["checks"][0], "status": "fail"})
    assert not check_record(r)["valid"]


def test_unknown_fields_and_claims_fail_closed():
    r = record("placement")
    r["automatic_permission_grant"] = True
    assert not check_record(r)["valid"]
    r.pop("automatic_permission_grant")
    r["claims"] = ["production_is_safe"]
    assert not check_record(r)["valid"]


def test_no_secrets_or_signed_urls_in_evidence():
    for ref in [
        "https://example.invalid/?token=private-value",
        "Bearer private-value",
        "auth-code:ABCDE-ABCDE",
    ]:
        r = record("placement")
        r["checks"][0]["evidence"] = [ref]
        report = check_record(r)
        assert not report["valid"]
        assert "private-value" not in json.dumps(report)


@pytest.mark.parametrize("value", ["yesterday", "2026-10-20T05:00:00", None])
def test_timestamp_requires_timezone(value):
    r = record()
    r["observed_at"] = value
    assert not check_record(r)["valid"]


def test_cli_is_read_only(tmp_path):
    p = tmp_path / "fixture.json"
    p.write_text(json.dumps(record("browser_approval", claims=["cli_authenticated"])))
    before = p.read_bytes()
    proc = subprocess.run(
        [sys.executable, "-m", "sillok.eval.evidence", "check", str(p)],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 1
    assert p.read_bytes() == before
    assert not list(tmp_path.glob("*.jsonl"))


def test_contract_and_checker_names_match():
    schema = json.loads(CONTRACT_PATH.read_text())
    claim_requirements, stages = ev.CLAIM_REQUIREMENTS, ev.STAGES
    assert set(schema["$defs"]["check"]["properties"]["stage"]["enum"]) == set(stages)
    assert set(schema["properties"]["claims"]["items"]["enum"]) == set(claim_requirements)


def test_get_is_not_token_exchange_and_progress_not_receipt():
    for claim in ["cli_authenticated", "transfer_verified", "remote_execution_verified"]:
        assert not check_record(record("network_request", claims=[claim]))["valid"]


@pytest.mark.parametrize(
    "field,value",
    [
        ("context", []),
        ("artifact", []),
        ("checks", {}),
        ("claims", {}),
        ("task_id", []),
        ("attempt_id", None),
    ],
)
def test_malformed_record_returns_errors_not_exception(field, value):
    r = record()
    r[field] = value
    assert not check_record(r)["valid"]


def test_nested_malformed_values_return_errors():
    for field in ["actor", "surface", "permission"]:
        r = record()
        r["context"][field] = []
        assert not check_record(r)["valid"]
    for field in ["status", "basis", "stage"]:
        r = record("placement")
        r["checks"][0][field] = []
        assert not check_record(r)["valid"]


def test_json_schema_semantic_map_matches_runtime():
    schema = json.loads(CONTRACT_PATH.read_text())
    assert schema["x-sillok-claim-requirements"] == {
        k: list(v) for k, v in ev.CLAIM_REQUIREMENTS.items()
    }


@pytest.mark.parametrize(
    "mutate",
    [
        lambda r: r.update(artifact=None),
        lambda r: r["artifact"].update(commit=1234567),
        lambda r: r["checks"][0].update(subject_sha256=None),
    ],
)
def test_json_null_and_numeric_commit_rejected(mutate):
    r = record("cli_auth")
    mutate(r)
    assert not check_record(r)["valid"]


def batch_record():
    """Synthetic two-item analogue of a frozen-catalog batch closeout."""
    base = record()
    return {k: v for k, v in base.items() if k not in ("artifact", "checks", "claims")} | {
        "schema_version": "execution-batch-v1",
        "scope": {"ref": "fixture:inventory", "sha256": "b" * 64},
        "expected_ids": ["entry-a", "entry-u"],
        "required_stages": ["recover", "validate", "register"],
        "receipts": [
            {
                "id": item,
                "stage": stage,
                "status": "pass",
                "basis": "observed",
                "evidence": [f"fixture:{item}/{stage}"],
            }
            for item in ("entry-a", "entry-u")
            for stage in ("recover", "validate", "register")
        ],
        "cleanup": {
            "required": True,
            "status": "pass",
            "basis": "observed",
            "evidence": ["fixture:normal-boot-security-and-shutdown"],
        },
        "pending": [],
        "data_complete": True,
        "final_complete": True,
    }


def batch_check(doc):
    return ev.check_batch(doc)


def test_batch_all_items_and_cleanup_complete():
    result = batch_check(batch_record())
    assert result["valid"] and result["final_complete"]
    assert result["expected_count"] == 2
    assert result["stage_counts"] == {"recover": 2, "validate": 2, "register": 2}
    assert result["verification_scope"] == "supplied-record-consistency-only"
    assert not result["executed_actions"]


@pytest.mark.parametrize(
    "mutation",
    [
        "last_item_only",
        "same_count_wrong_id",
        "duplicate",
        "failed",
        "inferred",
        "missing_evidence",
    ],
)
def test_batch_receipt_defects_cannot_claim_completion(mutation):
    doc = batch_record()
    if mutation == "last_item_only":
        doc["receipts"] = doc["receipts"][:3]
    elif mutation == "same_count_wrong_id":
        doc["receipts"][-1]["id"] = "outside-scope"
    elif mutation == "duplicate":
        doc["receipts"][-1] = dict(doc["receipts"][0])
    elif mutation == "failed":
        doc["receipts"][-1]["status"] = "fail"
    elif mutation == "inferred":
        doc["receipts"][-1]["basis"] = "inferred"
    else:
        doc["receipts"][-1]["evidence"] = []
    result = batch_check(doc)
    assert not result["valid"] and not result["final_complete"]


@pytest.mark.parametrize(
    "mutation",
    [
        "pending",
        "cleanup_missing",
        "cleanup_unverified",
        "cleanup_user_reported",
        "cleanup_no_evidence",
    ],
)
def test_batch_cleanup_and_pending_prevent_premature_close(mutation):
    doc = batch_record()
    if mutation == "pending":
        doc["pending"] = ["normal-boot-security-check"]
    elif mutation == "cleanup_missing":
        doc.pop("cleanup")
    elif mutation == "cleanup_unverified":
        doc["cleanup"]["status"] = "unverified"
    elif mutation == "cleanup_user_reported":
        doc["cleanup"]["basis"] = "user_reported"
    else:
        doc["cleanup"]["evidence"] = []
    result = batch_check(doc)
    assert not result["valid"] and not result["final_complete"]


def test_batch_partial_progress_and_data_only_are_valid_without_final_claim():
    doc = batch_record()
    doc.update(final_complete=False, pending=["cleanup"])
    doc["cleanup"].update(status="unverified", evidence=[])
    result = batch_check(doc)
    assert result["valid"] and result["data_complete"] and not result["final_complete"]
    doc.update(data_complete=False, receipts=doc["receipts"][:3])
    result = batch_check(doc)
    assert result["valid"] and not result["data_complete"]
    assert result["stage_counts"]["register"] == 1


@pytest.mark.parametrize(
    "field,value",
    [
        ("expected_ids", []),
        ("expected_ids", ["a", "a"]),
        ("expected_ids", [None]),
        ("required_stages", []),
        ("receipts", {}),
        ("cleanup", []),
        ("pending", [None]),
        ("data_complete", 1),
        ("final_complete", "yes"),
    ],
)
def test_batch_malformed_record_is_rejected_without_crash(field, value):
    doc = batch_record()
    doc[field] = value
    assert not batch_check(doc)["valid"]


def test_batch_checker_does_not_mutate_or_publish_secrets():
    doc = batch_record()
    before = json.dumps(doc, sort_keys=True)
    assert batch_check(doc) == batch_check(doc)
    assert json.dumps(doc, sort_keys=True) == before
    doc["receipts"][0]["evidence"] = ["https://invalid.example/?token=private-value"]
    result = batch_check(doc)
    assert not result["valid"] and "private-value" not in json.dumps(result)


def test_batch_cli_preserves_input_and_existing_v1(tmp_path):
    path = tmp_path / "batch.json"
    path.write_text(json.dumps(batch_record()))
    before = path.read_bytes()
    command = [sys.executable, "-m", "sillok.eval.evidence", "check-batch", str(path)]
    proc = subprocess.run(command, capture_output=True, text=True)
    assert proc.returncode == 0 and json.loads(proc.stdout)["final_complete"]
    assert path.read_bytes() == before
    assert check_record(record("cli_auth", claims=["cli_authenticated"]))["valid"]


def test_contract_file_matches_embedded_rules():
    r = ev.contract_consistency()
    assert r["valid"], r["errors"]


def test_tampered_contract_is_detected(tmp_path: Path):
    d = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    d["x-sillok-claim-requirements"]["release_verified"] = ["placement"]
    d["required"].remove("claims")
    d["properties"]["context"]["properties"]["surface"]["enum"].append("unlisted")
    p = tmp_path / "c.json"
    p.write_text(json.dumps(d), encoding="utf-8")
    errors = set(ev.contract_consistency(p)["errors"])
    assert {
        "contract:claim_requirements_mismatch",
        "contract:required_root_keys_mismatch",
        "contract:surface_enum_mismatch",
    } <= errors
    assert ev.contract_consistency(tmp_path / "missing.json")["errors"] == [
        "contract:unreadable_or_invalid_json"
    ]


def test_batch_contract_drift_is_detected(tmp_path: Path):
    d = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    d["$defs"]["batch"]["required"].remove("cleanup")
    p = tmp_path / "contract.json"
    p.write_text(json.dumps(d))
    assert "contract:batch_keys_mismatch" in ev.contract_consistency(p)["errors"]


def test_cli_contract_command():
    out = subprocess.run(
        [sys.executable, "-m", "sillok.eval.evidence", "contract"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert out.returncode == 0 and json.loads(out.stdout)["valid"]


def test_contract_ships_inside_the_package():
    assert CONTRACT_PATH.is_file() and CONTRACT_PATH.parent.name == "contracts"
