from __future__ import annotations

import json
import pathlib
from typing import Any

import pytest
from jsonschema import Draft202012Validator, ValidationError


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PRE_REQUEST_SCHEMA = REPO_ROOT / "contracts" / "github" / "github_executor_preflight_request.schema.json"
PRE_RESULT_SCHEMA = REPO_ROOT / "contracts" / "github" / "github_executor_preflight_result.schema.json"
EXECUTION_RESULT_SCHEMA = REPO_ROOT / "contracts" / "github" / "github_execution_result.schema.json"

REQUIRED_BLOCKER_CODES = {
    "github_auth_missing_or_invalid",
    "github_permission_insufficient",
    "github_repo_not_allowlisted",
    "github_branch_state_invalid",
    "github_file_state_conflict",
    "github_pr_state_conflict",
    "github_rate_limit_blocked",
    "github_network_error",
    "github_ci_ambiguity",
    "github_idempotency_conflict",
    "github_scope_drift",
    "github_secret_exposure",
    "github_authority_violation",
}

REQUIRED_CHECKS = {
    "repo_allowlist_check",
    "branch_state_check",
    "file_state_check",
    "pr_state_check",
    "auth_check",
    "permission_check",
    "rate_limit_check",
    "network_check",
    "ci_ambiguity_check",
    "idempotency_resume_check",
    "scope_check",
    "authority_check",
    "secret_exposure_check",
}


def _schema(path: pathlib.Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _blocker(code: str = "github_auth_missing_or_invalid") -> dict[str, str]:
    return {
        "code": code,
        "class": "auth" if code == "github_auth_missing_or_invalid" else "authority_violation",
        "message": "blocking evidence",
        "severity": "blocking",
    }


def _check(status: str = "pass") -> dict[str, Any]:
    return {"status": status, "evidence": ["checked"], "blocker_codes": []}


def _preflight_result(status: str = "pass") -> dict[str, Any]:
    checks = {name: _check("pass" if status == "pass" else "blocked") for name in REQUIRED_CHECKS}
    blockers = [] if status == "pass" else [_blocker("github_authority_violation")]
    return {
        "contract_version": "1.0.0",
        "request_id": "github-preflight-request-phase-17",
        "correlation_id": "corr-phase-17",
        "idempotency_key": "phase-17-idempotency-key",
        "status": status,
        "mutation_allowed": status == "pass",
        "repository_full_name": "Viktoryyyyy/flowiseai",
        "base_branch": "main",
        "target_branch": "flowiseai-pm/phase-17-github-executor-error-hardening-contracts",
        "approved_file_scope": [
            "contracts/github/github_executor_preflight_request.schema.json",
            "contracts/github/github_executor_preflight_result.schema.json",
            "contracts/github/github_execution_result.schema.json",
            "docs/orchestration/phase_17_github_executor_error_hardening.md",
            "tests/contract/test_phase_17_github_executor_contracts.py",
        ],
        "planned_operation": "create_or_update_approved_files",
        "blockers": blockers,
        "checks": checks,
        "hitl_approval": {
            "pm_l2_approval_status": "approved" if status == "pass" else "missing",
            "approval_ref": "pm-l2-phase-17-approved-scope",
        },
        "evidence": {
            "repo": "get_repo",
            "base_branch": "compare_commits main..main",
            "target_branch": "search_branches",
            "file_scope": ["approved scope checked"],
            "pull_request": None,
            "ci": None,
            "rate_limit": None,
        },
        "evaluated_at": "2026-06-29T00:00:00Z",
    }


def _execution_result() -> dict[str, Any]:
    return {
        "contract_version": "1.0.0",
        "execution_id": "github-execution-phase-17",
        "request_id": "github-preflight-request-phase-17",
        "correlation_id": "corr-phase-17",
        "idempotency_key": "phase-17-idempotency-key",
        "repository_full_name": "Viktoryyyyy/flowiseai",
        "base_branch": "main",
        "branch_name": "flowiseai-pm/phase-17-github-executor-error-hardening-contracts",
        "planned_operation": "create_or_update_approved_files",
        "preflight_status": "pass",
        "preflight_result_ref": "github-preflight-result-phase-17",
        "hitl_approval": {
            "approved": True,
            "approved_by_role": "PM_L2_PHASE_OWNER",
            "approval_ref": "pm-l2-phase-17-approved-scope",
        },
        "mutation_allowed": True,
        "status": "succeeded",
        "outcome": "completed",
        "blockers": [],
        "post_write_evidence": {
            "branch": "flowiseai-pm/phase-17-github-executor-error-hardening-contracts",
            "commit_sha": "0123456789abcdef0123456789abcdef01234567",
            "head_sha": "0123456789abcdef0123456789abcdef01234567",
            "changed_files": [
                "contracts/github/github_executor_preflight_request.schema.json",
                "contracts/github/github_executor_preflight_result.schema.json",
                "contracts/github/github_execution_result.schema.json",
                "docs/orchestration/phase_17_github_executor_error_hardening.md",
                "tests/contract/test_phase_17_github_executor_contracts.py",
            ],
            "pull_request": {
                "number": 18,
                "url": "https://github.com/Viktoryyyyy/flowiseai/pull/18",
                "state": "open",
            },
            "ci": {
                "workflow": "tests",
                "run_id": 1,
                "job": "contract-and-runtime-tests",
                "conclusion": "success",
                "evidence_tied_to_head_sha": True,
            },
        },
        "authority_boundary": {
            "merge_performed": False,
            "direct_main_write_performed": False,
            "force_push_performed": False,
            "delete_performed": False,
            "server_apply_performed": False,
            "deployment_performed": False,
            "flowise_graph_mutation_performed": False,
            "secrets_exposed": False,
        },
        "completed_at": "2026-06-29T00:01:00Z",
    }


def test_phase_17_schema_files_are_valid_draft_2020_12() -> None:
    for path in (PRE_REQUEST_SCHEMA, PRE_RESULT_SCHEMA, EXECUTION_RESULT_SCHEMA):
        schema = _schema(path)
        assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
        Draft202012Validator.check_schema(schema)


def test_required_blocker_code_enums_are_present() -> None:
    preflight_schema = _schema(PRE_RESULT_SCHEMA)
    execution_schema = _schema(EXECUTION_RESULT_SCHEMA)

    preflight_codes = set(preflight_schema["$defs"]["blocker"]["properties"]["code"]["enum"])
    execution_codes = set(execution_schema["$defs"]["blocker"]["properties"]["code"]["enum"])

    assert REQUIRED_BLOCKER_CODES <= preflight_codes
    assert REQUIRED_BLOCKER_CODES <= execution_codes


def test_preflight_status_cannot_pass_with_blockers() -> None:
    schema = _schema(PRE_RESULT_SCHEMA)
    validator = Draft202012Validator(schema)
    payload = _preflight_result("pass")

    validator.validate(payload)

    payload["blockers"] = [_blocker()]
    with pytest.raises(ValidationError):
        validator.validate(payload)


@pytest.mark.parametrize("check_status", ["failed", "blocked", "not_checked"])
def test_preflight_status_pass_requires_every_required_check_to_pass(check_status: str) -> None:
    schema = _schema(PRE_RESULT_SCHEMA)
    validator = Draft202012Validator(schema)
    payload = _preflight_result("pass")

    validator.validate(payload)

    payload["checks"]["auth_check"]["status"] = check_status
    with pytest.raises(ValidationError):
        validator.validate(payload)


def test_mutation_is_blocked_unless_preflight_status_is_pass() -> None:
    schema = _schema(EXECUTION_RESULT_SCHEMA)
    validator = Draft202012Validator(schema)
    payload = _execution_result()

    validator.validate(payload)

    payload["preflight_status"] = "blocked"
    payload["mutation_allowed"] = True
    payload["status"] = "blocked"
    payload["outcome"] = "blocked"
    payload["blockers"] = [_blocker("github_authority_violation")]

    with pytest.raises(ValidationError):
        validator.validate(payload)


def test_execution_succeeded_requires_pass_preflight_and_mutation_allowed() -> None:
    schema = _schema(EXECUTION_RESULT_SCHEMA)
    validator = Draft202012Validator(schema)
    payload = _execution_result()

    validator.validate(payload)

    payload["preflight_status"] = "blocked"
    payload["mutation_allowed"] = False
    payload["status"] = "succeeded"
    payload["outcome"] = "completed"
    payload["blockers"] = []

    with pytest.raises(ValidationError):
        validator.validate(payload)


def test_execution_completed_requires_pass_preflight_and_mutation_allowed() -> None:
    schema = _schema(EXECUTION_RESULT_SCHEMA)
    validator = Draft202012Validator(schema)
    payload = _execution_result()

    validator.validate(payload)

    payload["preflight_status"] = "blocked"
    payload["mutation_allowed"] = False
    payload["status"] = "skipped"
    payload["outcome"] = "completed"
    payload["blockers"] = []

    with pytest.raises(ValidationError):
        validator.validate(payload)


def test_hitl_pm_l2_approval_is_required_before_mutation() -> None:
    schema = _schema(EXECUTION_RESULT_SCHEMA)
    validator = Draft202012Validator(schema)
    payload = _execution_result()

    payload["hitl_approval"]["approved"] = False
    payload["mutation_allowed"] = True

    with pytest.raises(ValidationError):
        validator.validate(payload)


def test_post_write_evidence_fields_exist_in_execution_result_schema() -> None:
    schema = _schema(EXECUTION_RESULT_SCHEMA)
    evidence = schema["properties"]["post_write_evidence"]

    assert set(evidence["required"]) >= {
        "branch",
        "commit_sha",
        "head_sha",
        "changed_files",
        "pull_request",
        "ci",
    }
    assert set(evidence["properties"]["pull_request"]["required"]) == {"number", "url", "state"}
    assert set(evidence["properties"]["ci"]["required"]) == {
        "workflow",
        "run_id",
        "job",
        "conclusion",
        "evidence_tied_to_head_sha",
    }


def test_authority_violations_are_represented_as_blockers() -> None:
    preflight_schema = _schema(PRE_RESULT_SCHEMA)
    execution_schema = _schema(EXECUTION_RESULT_SCHEMA)

    assert "github_authority_violation" in preflight_schema["$defs"]["blocker"]["properties"]["code"]["enum"]
    assert "github_authority_violation" in execution_schema["$defs"]["blocker"]["properties"]["code"]["enum"]

    payload = _preflight_result("blocked")
    payload["blockers"] = [_blocker("github_authority_violation")]
    Draft202012Validator(preflight_schema).validate(payload)


def test_preflight_result_requires_all_error_class_checks() -> None:
    schema = _schema(PRE_RESULT_SCHEMA)
    required_checks = set(schema["properties"]["checks"]["required"])

    assert REQUIRED_CHECKS <= required_checks
