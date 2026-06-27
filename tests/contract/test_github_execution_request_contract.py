from __future__ import annotations

import copy
import json
import pathlib

import pytest
from jsonschema import Draft202012Validator, ValidationError

SCHEMA_DIR = pathlib.Path(__file__).resolve().parents[2] / "contracts" / "schemas"
SCHEMA_NAME = "github_execution_request.schema.json"

VALID_PAYLOAD = {
    "contract_version": "1.0.0",
    "request_id": "github-exec-001",
    "phase_run_id": "phase-2d-run-001",
    "requested_operation_type": "open_pull_request",
    "repository_full_name": "Viktoryyyyy/flowiseai",
    "base_ref": "origin/main",
    "base_sha": "3092cf6aea86676ea03d0d61f2e063f815145f18",
    "branch_name": "flowiseai-pm/universal-role-runner-contracts-phase-2d",
    "approved_file_scope": ["contracts/schemas/github_execution_request.schema.json"],
    "pr_metadata": {
        "title": "[flowiseai_pm_orchestration] Phase 2D Universal Role Runner contracts",
        "body_required": True,
        "base_branch": "main",
        "draft": False,
    },
    "ci_expectation": {"ci_required": True, "workflow_name": "tests", "evidence_must_match_head_sha": True},
    "result_evidence": {"commit_sha": None, "pr_number": None, "workflow_run_id": None, "conclusion": "not_started"},
    "safety_boundaries": {
        "direct_main_write_allowed": False,
        "server_apply_allowed": False,
        "deployment_allowed": False,
        "runtime_smoke_allowed": False,
        "secrets_allowed": False,
        "private_endpoints_allowed": False,
    },
    "secrets": [],
    "private_endpoints": [],
    "created_at": "2026-06-27T00:00:00Z",
    "metadata": {},
}


def load_schema() -> dict:
    with (SCHEMA_DIR / SCHEMA_NAME).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def assert_invalid(payload: dict) -> None:
    with pytest.raises(ValidationError):
        Draft202012Validator(load_schema()).validate(payload)


def test_github_execution_request_schema_is_valid_draft_2020_12() -> None:
    schema = load_schema()
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    Draft202012Validator.check_schema(schema)


def test_valid_github_execution_request_payload_passes() -> None:
    Draft202012Validator(load_schema()).validate(VALID_PAYLOAD)


def test_missing_required_github_execution_request_field_fails() -> None:
    payload = copy.deepcopy(VALID_PAYLOAD)
    payload.pop("request_id")
    assert_invalid(payload)


def test_additional_github_execution_request_property_fails() -> None:
    payload = copy.deepcopy(VALID_PAYLOAD)
    payload["unexpected"] = "forbidden"
    assert_invalid(payload)


def test_unknown_github_execution_request_operation_fails() -> None:
    payload = copy.deepcopy(VALID_PAYLOAD)
    payload["requested_operation_type"] = "push_to_main"
    assert_invalid(payload)


def test_github_execution_request_rejects_server_apply_authority() -> None:
    payload = copy.deepcopy(VALID_PAYLOAD)
    payload["safety_boundaries"]["server_apply_allowed"] = True
    assert_invalid(payload)


def test_github_execution_request_rejects_secrets_and_private_endpoints() -> None:
    payload = copy.deepcopy(VALID_PAYLOAD)
    payload["secrets"] = ["placeholder-secret"]
    assert_invalid(payload)
    payload = copy.deepcopy(VALID_PAYLOAD)
    payload["private_endpoints"] = ["private-service"]
    assert_invalid(payload)
