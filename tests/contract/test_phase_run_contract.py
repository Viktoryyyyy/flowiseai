from __future__ import annotations

import copy
import json
import pathlib

import pytest
from jsonschema import Draft202012Validator, ValidationError

SCHEMA_DIR = pathlib.Path(__file__).resolve().parents[2] / "contracts" / "schemas"
SCHEMA_NAME = "phase_run.schema.json"

VALID_PAYLOAD = {
    "contract_version": "1.0.0",
    "phase_run_id": "phase-2d-run-001",
    "project": "MOEX Bot",
    "lane": "flowiseai_pm_orchestration",
    "execution_mode": "browser_chatgpt_github_direct",
    "source_repository": {"repository_full_name": "Viktoryyyyy/flowiseai", "default_branch": "main"},
    "base_ref": "origin/main",
    "base_sha": "3092cf6aea86676ea03d0d61f2e063f815145f18",
    "branch_refs": {
        "approved_branch_name": "flowiseai-pm/universal-role-runner-contracts-phase-2d",
        "active_branch_name": "flowiseai-pm/universal-role-runner-contracts-phase-2d",
    },
    "pr_refs": {"active_pr_number": 1, "active_pr_head_sha": "3092cf6aea86676ea03d0d61f2e063f815145f18"},
    "authority_boundary": {
        "merge_authority": "PM_L2_ONLY",
        "direct_main_write_allowed": False,
        "server_apply_authority": "blocked_until_explicit_future_phase",
        "runtime_allowed": False,
        "deployment_allowed": False,
        "runtime_smoke_allowed": False,
        "secrets_allowed": False,
    },
    "lifecycle_state": "pr_open",
    "status": "active",
    "timestamps": {"created_at": "2026-06-27T00:00:00Z", "updated_at": "2026-06-27T00:00:00Z", "completed_at": None},
    "blockers": [],
    "metadata": {"phase": "2D"},
}


def load_schema() -> dict:
    with (SCHEMA_DIR / SCHEMA_NAME).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def assert_invalid(payload: dict) -> None:
    with pytest.raises(ValidationError):
        Draft202012Validator(load_schema()).validate(payload)


def test_phase_run_schema_is_valid_draft_2020_12() -> None:
    schema = load_schema()
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    Draft202012Validator.check_schema(schema)


def test_valid_phase_run_payload_passes() -> None:
    Draft202012Validator(load_schema()).validate(VALID_PAYLOAD)


def test_missing_required_phase_run_field_fails() -> None:
    payload = copy.deepcopy(VALID_PAYLOAD)
    payload.pop("phase_run_id")
    assert_invalid(payload)


def test_additional_phase_run_property_fails() -> None:
    payload = copy.deepcopy(VALID_PAYLOAD)
    payload["unexpected"] = "forbidden"
    assert_invalid(payload)


def test_unknown_phase_run_status_value_fails() -> None:
    payload = copy.deepcopy(VALID_PAYLOAD)
    payload["status"] = "unknown_status"
    assert_invalid(payload)


def test_phase_run_authority_boundary_prevents_direct_main_write() -> None:
    payload = copy.deepcopy(VALID_PAYLOAD)
    payload["authority_boundary"]["direct_main_write_allowed"] = True
    assert_invalid(payload)


def test_phase_run_rejects_runtime_deployment_or_smoke_authority() -> None:
    for field in ["runtime_allowed", "deployment_allowed", "runtime_smoke_allowed"]:
        payload = copy.deepcopy(VALID_PAYLOAD)
        payload["authority_boundary"][field] = True
        assert_invalid(payload)
