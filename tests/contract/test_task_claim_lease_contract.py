from __future__ import annotations

import copy
import json
import pathlib

import pytest
from jsonschema import Draft202012Validator, ValidationError

SCHEMA_DIR = pathlib.Path(__file__).resolve().parents[2] / "contracts" / "schemas"
SCHEMA_NAME = "task_claim_lease.schema.json"

VALID_PAYLOAD = {
    "contract_version": "1.0.0",
    "lease_id": "lease-001",
    "role_task_id": "role-task-001",
    "claimant_role": "SUBCHAT_IMPLEMENTATION",
    "claimant_id": "worker-001",
    "lease_state": "active",
    "claimed_at": "2026-06-27T00:00:00Z",
    "expires_at": "2026-06-27T00:15:00Z",
    "renewed_at": None,
    "released_at": None,
    "expiration_semantics": {
        "expires_without_renewal": True,
        "expired_tasks_are_reclaimable": True,
        "release_after_expiry_allowed": False,
    },
    "metadata": {},
}


def load_schema() -> dict:
    with (SCHEMA_DIR / SCHEMA_NAME).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def assert_invalid(payload: dict) -> None:
    with pytest.raises(ValidationError):
        Draft202012Validator(load_schema()).validate(payload)


def test_task_claim_lease_schema_is_valid_draft_2020_12() -> None:
    schema = load_schema()
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    Draft202012Validator.check_schema(schema)


def test_valid_task_claim_lease_payload_passes() -> None:
    Draft202012Validator(load_schema()).validate(VALID_PAYLOAD)


def test_missing_required_task_claim_lease_field_fails() -> None:
    payload = copy.deepcopy(VALID_PAYLOAD)
    payload.pop("lease_id")
    assert_invalid(payload)


def test_additional_task_claim_lease_property_fails() -> None:
    payload = copy.deepcopy(VALID_PAYLOAD)
    payload["unexpected"] = "forbidden"
    assert_invalid(payload)


def test_unknown_task_claim_lease_state_value_fails() -> None:
    payload = copy.deepcopy(VALID_PAYLOAD)
    payload["lease_state"] = "unknown_state"
    assert_invalid(payload)


def test_task_claim_lease_rejects_release_after_expiry() -> None:
    payload = copy.deepcopy(VALID_PAYLOAD)
    payload["expiration_semantics"]["release_after_expiry_allowed"] = True
    assert_invalid(payload)
