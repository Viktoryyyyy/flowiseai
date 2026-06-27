from __future__ import annotations

import copy
import json
import pathlib

import pytest
from jsonschema import Draft202012Validator, ValidationError

SCHEMA_DIR = pathlib.Path(__file__).resolve().parents[2] / "contracts" / "schemas"
SCHEMA_NAME = "pm_l3_decision.schema.json"

VALID_PAYLOAD = {
    "contract_version": "1.0.0",
    "decision_id": "decision-001",
    "phase_run_id": "phase-2d-run-001",
    "decision_type": "route_next_role",
    "next_role": "SUBCHAT_VALIDATION",
    "next_task": {"task_id": "validate-phase-2d-pr"},
    "routing_target": {"target_role": "SUBCHAT_VALIDATION", "target_queue": "browser_chat", "handoff_required": True},
    "acceptance_details": {"accepted": False, "criteria_met": []},
    "rejection_details": {"rejected": False, "reasons": []},
    "blocker_details": {"blocked": False, "blockers": []},
    "created_at": "2026-06-27T00:00:00Z",
    "metadata": {},
}


def load_schema() -> dict:
    with (SCHEMA_DIR / SCHEMA_NAME).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def assert_invalid(payload: dict) -> None:
    with pytest.raises(ValidationError):
        Draft202012Validator(load_schema()).validate(payload)


def test_pm_l3_decision_schema_is_valid_draft_2020_12() -> None:
    schema = load_schema()
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    Draft202012Validator.check_schema(schema)


def test_valid_pm_l3_decision_payload_passes() -> None:
    Draft202012Validator(load_schema()).validate(VALID_PAYLOAD)


def test_missing_required_pm_l3_decision_field_fails() -> None:
    payload = copy.deepcopy(VALID_PAYLOAD)
    payload.pop("decision_id")
    assert_invalid(payload)


def test_additional_pm_l3_decision_property_fails() -> None:
    payload = copy.deepcopy(VALID_PAYLOAD)
    payload["unexpected"] = "forbidden"
    assert_invalid(payload)


def test_unknown_pm_l3_decision_type_fails() -> None:
    payload = copy.deepcopy(VALID_PAYLOAD)
    payload["decision_type"] = "unknown_decision"
    assert_invalid(payload)


def test_pm_l3_decision_rejects_server_routing_target() -> None:
    payload = copy.deepcopy(VALID_PAYLOAD)
    payload["routing_target"]["target_queue"] = "server"
    assert_invalid(payload)
