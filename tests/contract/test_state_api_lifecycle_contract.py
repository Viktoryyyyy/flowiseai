from __future__ import annotations

import json
import pathlib
from typing import Any

import yaml


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


def load_json(path: str) -> dict[str, Any]:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def load_yaml(path: str) -> dict[str, Any]:
    data = yaml.safe_load((REPO_ROOT / path).read_text(encoding="utf-8"))
    assert isinstance(data, dict), path
    return data


def schema_allowed_transitions() -> dict[str, list[str]]:
    schema = load_json("contracts/schemas/state-transition.schema.json")
    properties = schema["properties"]["allowed_transitions"]["properties"]
    return {state: properties[state]["const"] for state in EXPECTED_ALLOWED_TRANSITIONS}


def yaml_allowed_transitions() -> dict[str, list[str]]:
    data = load_yaml("state_api/runtime_stub/state_api_contract.yaml")
    return data["lifecycle"]["allowed_transitions"]


def test_allowed_lifecycle_transitions_are_explicit_in_schema() -> None:
    assert schema_allowed_transitions() == EXPECTED_ALLOWED_TRANSITIONS


def test_allowed_lifecycle_transitions_are_explicit_in_yaml_contract() -> None:
    assert yaml_allowed_transitions() == EXPECTED_ALLOWED_TRANSITIONS


def test_forbidden_transitions_are_not_listed() -> None:
    allowed = schema_allowed_transitions()
    all_states = set(EXPECTED_ALLOWED_TRANSITIONS)
    for from_state, targets in allowed.items():
        forbidden_targets = all_states - set(targets)
        for target in forbidden_targets:
            assert target not in targets, f"{from_state}->{target}"


def test_terminal_states_have_no_outgoing_transitions() -> None:
    allowed = schema_allowed_transitions()
    for terminal_state in TERMINAL_STATES:
        assert allowed[terminal_state] == []
