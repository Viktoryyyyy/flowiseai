from __future__ import annotations

import pathlib

import yaml


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
REQUIRED_OPERATIONS = {
    "create_task",
    "read_task",
    "transition_task_state",
    "claim_next_task",
    "renew_task_lease",
    "release_task_lease",
    "persist_handoff",
    "persist_role_output",
    "append_audit_event",
    "read_state_snapshot",
}
REQUIRED_RESOURCES = {"Task", "Handoff", "RoleOutput", "AuditEvent", "TaskClaimLease", "StateSnapshot"}
REQUIRED_SCHEMA_REFS = {
    "task",
    "handoff",
    "role_output",
    "audit_event",
    "task_lease",
    "state_snapshot",
    "state_transition",
    "idempotency_record",
}


def load_state_api_contract() -> dict:
    data = yaml.safe_load((REPO_ROOT / "state_api/runtime_stub/state_api_contract.yaml").read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def test_required_operations_are_represented_in_state_api_contract() -> None:
    data = load_state_api_contract()
    assert set(data["operations"]) == REQUIRED_OPERATIONS
    assert set(data["abstract_operations"]) == REQUIRED_OPERATIONS


def test_required_resources_and_schema_refs_are_represented() -> None:
    data = load_state_api_contract()
    assert REQUIRED_RESOURCES.issubset(data["resources"])
    assert REQUIRED_SCHEMA_REFS.issubset(data["schema_refs"])


def test_mutating_operations_have_idempotency_contract() -> None:
    data = load_state_api_contract()
    mutating_operations = {name for name, spec in data["operations"].items() if spec["mutating"] is True}
    assert set(data["idempotency_model"]["mutating_operations"]) == mutating_operations
    for operation_name in mutating_operations:
        assert data["operations"][operation_name]["idempotent"] is True


def test_state_api_contract_remains_runtime_neutral() -> None:
    data = load_state_api_contract()
    assert data["runtime_claim"] is False
    assert data["implementation_status"] == "none"
    assert data["design_scope"]["runtime_service"] is False
    assert data["design_scope"]["deployment_selected"] is False
    assert data["runtime_boundary"]["server_url"] == "none"
    assert data["runtime_boundary"]["db_engine"] == "not_selected"


def test_retry_representation_uses_task_metadata_plus_audit_event_only() -> None:
    data = load_state_api_contract()
    assert data["retry_failure_model"]["representation"] == "Task metadata plus AuditEvent only"
    assert data["retry_failure_model"]["retry_record_schema"] == "not_created"
    assert "retry-record.schema.json" not in "\n".join(data["schema_refs"].values())
