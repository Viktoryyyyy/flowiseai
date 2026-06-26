from __future__ import annotations

import json
import pathlib
from typing import Any

import pytest
import yaml
from jsonschema import Draft202012Validator, ValidationError


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
EXPECTED_ALLOWED_TRANSITIONS = {
    "created": ["assigned", "blocked", "failed"],
    "assigned": ["running", "blocked", "failed"],
    "running": ["assigned", "blocked", "completed", "validation_pending", "failed"],
    "blocked": ["assigned", "failed"],
    "completed": ["validation_pending", "validated"],
    "validation_pending": ["validated", "blocked", "failed"],
    "validated": [],
    "failed": [],
}
TERMINAL_STATES = {"validated", "failed"}
ALLOWED_TRANSITION_PAIRS = [
    (from_state, to_state)
    for from_state, targets in EXPECTED_ALLOWED_TRANSITIONS.items()
    for to_state in targets
]
FORBIDDEN_TRANSITION_PAIRS = [
    ("validated", "created"),
    ("failed", "assigned"),
    ("created", "validated"),
    ("completed", "running"),
]


def load_json(path: str) -> dict[str, Any]:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def load_yaml(path: str) -> dict[str, Any]:
    data = yaml.safe_load((REPO_ROOT / path).read_text(encoding="utf-8"))
    assert isinstance(data, dict), path
    return data


def load_state_transition_schema() -> dict[str, Any]:
    return load_json("contracts/schemas/state-transition.schema.json")


def state_transition_validator() -> Draft202012Validator:
    return Draft202012Validator(load_state_transition_schema())


def schema_allowed_transitions() -> dict[str, list[str]]:
    schema = load_state_transition_schema()
    properties = schema["properties"]["allowed_transitions"]["properties"]
    return {state: properties[state]["const"] for state in EXPECTED_ALLOWED_TRANSITIONS}


def yaml_allowed_transitions() -> dict[str, list[str]]:
    data = load_yaml("state_api/runtime_stub/state_api_contract.yaml")
    return data["lifecycle"]["allowed_transitions"]


def minimal_transition_instance(from_state: str, to_state: str) -> dict[str, Any]:
    return {
        "transition_id": f"transition-{from_state}-{to_state}",
        "schema_version": "1.0.0",
        "task_id": "task-001",
        "from_state": from_state,
        "to_state": to_state,
        "actor_role": "PM_L3_DELIVERY_VALIDATION_OWNER",
        "occurred_at": "2026-06-26T00:00:00Z",
        "allowed_transitions": EXPECTED_ALLOWED_TRANSITIONS,
        "terminal_states": ["validated", "failed"],
        "runtime_claim": False,
    }


def test_allowed_lifecycle_transitions_are_explicit_in_schema() -> None:
    assert schema_allowed_transitions() == EXPECTED_ALLOWED_TRANSITIONS


def test_allowed_lifecycle_transitions_are_explicit_in_yaml_contract() -> None:
    assert yaml_allowed_transitions() == EXPECTED_ALLOWED_TRANSITIONS


@pytest.mark.parametrize(("from_state", "to_state"), ALLOWED_TRANSITION_PAIRS)
def test_allowed_transition_instances_validate(from_state: str, to_state: str) -> None:
    state_transition_validator().validate(minimal_transition_instance(from_state, to_state))


def test_forbidden_transitions_are_not_listed() -> None:
    validator = state_transition_validator()

    for from_state, to_state in FORBIDDEN_TRANSITION_PAIRS:
        assert to_state not in EXPECTED_ALLOWED_TRANSITIONS[from_state]
        with pytest.raises(ValidationError):
            validator.validate(minimal_transition_instance(from_state, to_state))


@pytest.mark.parametrize(("from_state", "to_state"), FORBIDDEN_TRANSITION_PAIRS)
def test_forbidden_transition_instances_are_rejected(
    from_state: str, to_state: str
) -> None:
    with pytest.raises(ValidationError):
        state_transition_validator().validate(
            minimal_transition_instance(from_state, to_state)
        )


def test_terminal_states_have_no_outgoing_transitions() -> None:
    allowed = schema_allowed_transitions()
    yaml_allowed = yaml_allowed_transitions()
    validator = state_transition_validator()

    for terminal_state in TERMINAL_STATES:
        assert EXPECTED_ALLOWED_TRANSITIONS[terminal_state] == []
        assert allowed[terminal_state] == []
        assert yaml_allowed[terminal_state] == []
        for target_state in EXPECTED_ALLOWED_TRANSITIONS:
            with pytest.raises(ValidationError):
                validator.validate(
                    minimal_transition_instance(terminal_state, target_state)
                )
