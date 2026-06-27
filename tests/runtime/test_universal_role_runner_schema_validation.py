from __future__ import annotations

import copy

import pytest

from universal_role_runner import (
    BoundaryViolationError,
    UniversalRoleRunner,
    build_github_execution_request,
    build_pm_l3_decision_role_output,
    build_role_output,
    build_role_task,
    validate_github_execution_request,
    validate_pm_l3_decision,
    validate_role_output,
    validate_role_task,
)
from universal_role_runner.models import SchemaValidationError


CREATED_AT = "2026-06-27T00:00:00Z"
BASE_SHA = "f6b88fd7b617d400173b417e55916d93f53a3baf"


def valid_role_task() -> dict:
    return build_role_task(
        role_task_id="role-task-schema",
        phase_run_id="phase-run-2e",
        lane="flowiseai_pm_orchestration",
        assigned_role="SUBCHAT_IMPLEMENTATION",
        approved_scope=["universal_role_runner/**"],
        forbidden_scope=["state_api/runtime/**", "contracts/schemas/**"],
        acceptance_criteria=["schema validation rejects invalid payloads"],
        created_at=CREATED_AT,
    )


def valid_role_output() -> dict:
    return build_role_output(
        role_output_id="role-output-schema",
        role_task_id="role-task-schema",
        producing_role="SUBCHAT_IMPLEMENTATION",
        output_type="implementation_report",
        payload={"status": "pass"},
        created_at=CREATED_AT,
    )


def valid_pm_l3_decision() -> dict:
    return {
        "contract_version": "1.0.0",
        "decision_id": "decision-schema",
        "phase_run_id": "phase-run-2e",
        "decision_type": "complete_phase_step",
        "next_role": None,
        "next_task": None,
        "routing_target": {
            "target_role": None,
            "target_queue": "none",
            "handoff_required": False,
        },
        "acceptance_details": {
            "accepted": True,
            "criteria_met": ["tests passed"],
        },
        "rejection_details": {
            "rejected": False,
            "reasons": [],
        },
        "blocker_details": {
            "blocked": False,
            "blockers": [],
        },
        "created_at": CREATED_AT,
    }


def valid_github_request() -> dict:
    return build_github_execution_request(
        request_id="github-request-schema",
        phase_run_id="phase-run-2e",
        requested_operation_type="commit_approved_scope",
        repository_full_name="Viktoryyyyy/flowiseai",
        base_ref="main",
        base_sha=BASE_SHA,
        branch_name="flowiseai-pm/universal-role-runner-runtime-phase-2e",
        approved_file_scope=["universal_role_runner/**"],
        pr_title="[flowiseai_pm_orchestration] Phase 2E Universal Role Runner local/dev runtime",
        created_at=CREATED_AT,
    )


def test_schema_validators_accept_valid_payloads() -> None:
    assert validate_role_task(valid_role_task())["role_task_id"] == "role-task-schema"
    assert validate_role_output(valid_role_output())["role_output_id"] == "role-output-schema"
    assert validate_pm_l3_decision(valid_pm_l3_decision())["decision_id"] == "decision-schema"
    assert validate_github_execution_request(valid_github_request())["request_id"] == "github-request-schema"


@pytest.mark.parametrize(
    ("factory", "mutator"),
    [
        (valid_role_task, lambda payload: payload.pop("approved_scope")),
        (valid_role_output, lambda payload: payload["structured_payload"].update({"output_type": "unsupported"})),
        (valid_pm_l3_decision, lambda payload: payload.update({"decision_type": "unsupported"})),
        (valid_github_request, lambda payload: payload["safety_boundaries"].update({"server_apply_allowed": True})),
    ],
)
def test_schema_validators_reject_invalid_payloads(factory, mutator) -> None:
    payload = copy.deepcopy(factory())
    mutator(payload)

    with pytest.raises(SchemaValidationError):
        if "role_task_id" in payload:
            validate_role_task(payload)
        elif "role_output_id" in payload:
            validate_role_output(payload)
        elif "decision_id" in payload:
            validate_pm_l3_decision(payload)
        else:
            validate_github_execution_request(payload)


def test_pm_l3_decision_role_output_must_use_decision_report() -> None:
    role_output = build_pm_l3_decision_role_output(
        decision=valid_pm_l3_decision(),
        role_task_id="role-task-schema",
        role_output_id="role-output-decision-schema",
        created_at=CREATED_AT,
    )
    assert role_output["structured_payload"]["output_type"] == "decision_report"


def test_github_execution_request_execution_fails_closed(operations) -> None:
    runner = UniversalRoleRunner(operations)
    request = valid_github_request()

    with pytest.raises(BoundaryViolationError):
        runner.reject_github_execution_request(request, attempted_action="server_apply")
