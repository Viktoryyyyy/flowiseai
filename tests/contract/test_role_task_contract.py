from __future__ import annotations

import copy
import json
import pathlib

import pytest
from jsonschema import Draft202012Validator, ValidationError

SCHEMA_DIR = pathlib.Path(__file__).resolve().parents[2] / "contracts" / "schemas"
SCHEMA_NAME = "role_task.schema.json"

VALID_PAYLOAD = {
    "contract_version": "1.0.0",
    "role_task_id": "role-task-001",
    "phase_run_id": "phase-2d-run-001",
    "project": "MOEX Bot",
    "lane": "flowiseai_pm_orchestration",
    "execution_mode": "browser_chatgpt_github_direct",
    "assigned_role": "SUBCHAT_IMPLEMENTATION",
    "input_context": {
        "context_delivery_mode": "inline_copy_block",
        "role_context_ref": "SUBCHAT_IMPLEMENTATION",
        "dynamic_context": {"task_id": "flowiseai_phase_2d_universal_role_runner_contracts_implementation"},
    },
    "approved_scope": ["contracts/schemas/role_task.schema.json"],
    "forbidden_scope": ["README.md"],
    "acceptance_criteria": ["schema validates"],
    "lease_ref": {"required": True, "lease_id": "lease-001"},
    "status": "claimed",
    "retry_metadata": {"attempt_count": 0, "max_attempts": 2, "retry_state": "not_retryable", "last_failure_code": None},
    "output_ref": {"role_output_id": None, "immutable": True},
    "created_at": "2026-06-27T00:00:00Z",
    "updated_at": None,
    "metadata": {},
}


def load_schema() -> dict:
    with (SCHEMA_DIR / SCHEMA_NAME).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def assert_invalid(payload: dict) -> None:
    with pytest.raises(ValidationError):
        Draft202012Validator(load_schema()).validate(payload)


def test_role_task_schema_is_valid_draft_2020_12() -> None:
    schema = load_schema()
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    Draft202012Validator.check_schema(schema)


def test_valid_role_task_payload_passes() -> None:
    Draft202012Validator(load_schema()).validate(VALID_PAYLOAD)


def test_missing_required_role_task_field_fails() -> None:
    payload = copy.deepcopy(VALID_PAYLOAD)
    payload.pop("role_task_id")
    assert_invalid(payload)


def test_additional_role_task_property_fails() -> None:
    payload = copy.deepcopy(VALID_PAYLOAD)
    payload["unexpected"] = "forbidden"
    assert_invalid(payload)


def test_unknown_role_task_status_value_fails() -> None:
    payload = copy.deepcopy(VALID_PAYLOAD)
    payload["status"] = "unknown_status"
    assert_invalid(payload)


def test_role_task_output_ref_is_immutable() -> None:
    payload = copy.deepcopy(VALID_PAYLOAD)
    payload["output_ref"]["immutable"] = False
    assert_invalid(payload)
