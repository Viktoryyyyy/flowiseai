from __future__ import annotations

import copy
import json
import pathlib

import pytest
from jsonschema import Draft202012Validator, ValidationError

SCHEMA_DIR = pathlib.Path(__file__).resolve().parents[2] / "contracts" / "schemas"
SCHEMA_NAME = "role_output.schema.json"

VALID_PAYLOAD = {
    "contract_version": "1.0.0",
    "role_output_id": "role-output-001",
    "role_task_id": "role-task-001",
    "producing_role": "SUBCHAT_IMPLEMENTATION",
    "structured_payload": {
        "output_type": "implementation_report",
        "payload": {"branch_name": "flowiseai-pm/universal-role-runner-contracts-phase-2d"},
    },
    "validation_status": "schema_valid",
    "immutable_persistence": {
        "persisted": True,
        "persistence_marker": "append_only_role_output",
        "mutation_policy": "append_new_version_only",
        "replacement_policy": "forbidden",
    },
    "evidence_refs": [{"ref_type": "commit", "ref": "head", "head_sha": "3092cf6aea86676ea03d0d61f2e063f815145f18"}],
    "blockers": [],
    "created_at": "2026-06-27T00:00:00Z",
    "metadata": {},
}


def load_schema() -> dict:
    with (SCHEMA_DIR / SCHEMA_NAME).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def assert_invalid(payload: dict) -> None:
    with pytest.raises(ValidationError):
        Draft202012Validator(load_schema()).validate(payload)


def test_role_output_schema_is_valid_draft_2020_12() -> None:
    schema = load_schema()
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    Draft202012Validator.check_schema(schema)


def test_valid_role_output_payload_passes() -> None:
    Draft202012Validator(load_schema()).validate(VALID_PAYLOAD)


def test_missing_required_role_output_field_fails() -> None:
    payload = copy.deepcopy(VALID_PAYLOAD)
    payload.pop("role_output_id")
    assert_invalid(payload)


def test_additional_role_output_property_fails() -> None:
    payload = copy.deepcopy(VALID_PAYLOAD)
    payload["unexpected"] = "forbidden"
    assert_invalid(payload)


def test_unknown_role_output_validation_status_fails() -> None:
    payload = copy.deepcopy(VALID_PAYLOAD)
    payload["validation_status"] = "unknown_status"
    assert_invalid(payload)


def test_role_output_rejects_mutable_replacement_policy() -> None:
    payload = copy.deepcopy(VALID_PAYLOAD)
    payload["immutable_persistence"]["replacement_policy"] = "allowed"
    assert_invalid(payload)


def test_role_output_is_persisted_immutable_output_not_mutable_conversation_state() -> None:
    payload = copy.deepcopy(VALID_PAYLOAD)
    payload["immutable_persistence"]["persistence_marker"] = "mutable_conversation_state"
    assert_invalid(payload)
