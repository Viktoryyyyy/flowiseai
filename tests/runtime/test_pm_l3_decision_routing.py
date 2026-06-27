from __future__ import annotations

import pytest

from universal_role_runner import PMDecisionRoutingError, route_pm_l3_decision


CREATED_AT = "2026-06-27T00:00:00Z"


def _blocker(code: str = "scope_blocked") -> dict:
    return {"code": code, "message": "scope widening required", "severity": "blocking"}


def _decision(
    decision_type: str,
    *,
    next_role: str | None = None,
    next_task: dict | None = None,
    target_role: str | None = None,
    target_queue: str = "none",
    handoff_required: bool = False,
    accepted: bool = False,
    criteria_met: list[str] | None = None,
    rejected: bool = False,
    reasons: list[str] | None = None,
    blocked: bool = False,
    blockers: list[dict] | None = None,
) -> dict:
    return {
        "pm_l3_decision": {
            "contract_version": "1.0.0",
            "decision_id": f"decision-{decision_type}",
            "phase_run_id": "phase-run-3",
            "decision_type": decision_type,
            "next_role": next_role,
            "next_task": next_task,
            "routing_target": {
                "target_role": target_role,
                "target_queue": target_queue,
                "handoff_required": handoff_required,
            },
            "acceptance_details": {
                "accepted": accepted,
                "criteria_met": criteria_met or [],
            },
            "rejection_details": {
                "rejected": rejected,
                "reasons": reasons or [],
            },
            "blocker_details": {
                "blocked": blocked,
                "blockers": blockers or [],
            },
            "created_at": CREATED_AT,
        }
    }


def test_route_next_role_produces_role_task_request_artifact() -> None:
    result = route_pm_l3_decision(
        _decision(
            "route_next_role",
            next_role="SUBCHAT_IMPLEMENTATION",
            next_task={"task_id": "phase-3a-implementation"},
            target_role="SUBCHAT_IMPLEMENTATION",
            target_queue="browser_chat",
            handoff_required=True,
        )
    )

    assert result["routing_status"] == "routed"
    assert result["next_action"] == "create_or_persist_role_task"
    assert result["target_role"] == "SUBCHAT_IMPLEMENTATION"
    assert result["target_queue"] == "browser_chat"
    assert result["handoff_required"] is True
    assert result["next_step_artifact"]["artifact_type"] == "role_task_request"
    assert result["next_step_artifact"]["next_task"] == {"task_id": "phase-3a-implementation"}
    assert result["next_step_artifact"]["side_effects"] == {
        "github_mutation_executed": False,
        "server_apply_executed": False,
        "deployment_executed": False,
        "runtime_smoke_executed": False,
    }


@pytest.mark.parametrize(
    ("decision_type", "expected_status", "expected_action", "artifact_type"),
    [
        ("accept_role_output", "accepted", "record_decision", "role_output_acceptance"),
        ("reject_role_output", "rejected", "record_decision", "role_output_rejection"),
        ("raise_blocker", "blocked", "record_blocker_and_stop", "blocker_escalation"),
        ("return_to_pm_l2", "returned_to_pm_l2", "generate_pm_l2_handoff", "pm_l2_return_package_request"),
        ("complete_phase_step", "phase_step_completed", "record_phase_step_completion", "phase_step_completion_record"),
    ],
)
def test_supported_non_role_routing_decisions_produce_deterministic_artifacts(
    decision_type: str,
    expected_status: str,
    expected_action: str,
    artifact_type: str,
) -> None:
    decision = _decision(decision_type)
    if decision_type in {"accept_role_output", "complete_phase_step"}:
        decision["pm_l3_decision"]["acceptance_details"] = {
            "accepted": True,
            "criteria_met": ["repo-local criteria met"],
        }
    if decision_type == "reject_role_output":
        decision["pm_l3_decision"]["rejection_details"] = {
            "rejected": True,
            "reasons": ["missing CI evidence"],
        }
    if decision_type == "raise_blocker":
        decision["pm_l3_decision"]["blocker_details"] = {
            "blocked": True,
            "blockers": [_blocker()],
        }
    if decision_type == "return_to_pm_l2":
        decision["pm_l3_decision"]["routing_target"] = {
            "target_role": "PM_L2_PHASE_OWNER",
            "target_queue": "pm_l2_return",
            "handoff_required": True,
        }

    result = route_pm_l3_decision(decision)

    assert result["routing_status"] == expected_status
    assert result["next_action"] == expected_action
    assert result["next_step_artifact"]["artifact_type"] == artifact_type
    assert result["next_step_artifact"]["decision_type"] == decision_type


def test_request_correction_requires_routeable_next_task() -> None:
    result = route_pm_l3_decision(
        _decision(
            "request_correction",
            next_role="SUBCHAT_IMPLEMENTATION",
            next_task={"task_id": "correct-phase-3a-output"},
            target_role="SUBCHAT_IMPLEMENTATION",
            target_queue="n8n_role_task_queue",
            handoff_required=True,
            rejected=True,
            reasons=["validation failed"],
        )
    )

    assert result["routing_status"] == "correction_requested"
    assert result["next_action"] == "route_correction_task"
    assert result["next_step_artifact"]["artifact_type"] == "correction_request"


def test_route_next_role_rejects_missing_next_task() -> None:
    with pytest.raises(PMDecisionRoutingError) as exc:
        route_pm_l3_decision(
            _decision(
                "route_next_role",
                next_role="SUBCHAT_IMPLEMENTATION",
                target_role="SUBCHAT_IMPLEMENTATION",
                target_queue="browser_chat",
                handoff_required=True,
            )
        )

    assert exc.value.details["decision_type"] == "route_next_role"


def test_return_to_pm_l2_rejects_wrong_queue() -> None:
    with pytest.raises(PMDecisionRoutingError):
        route_pm_l3_decision(
            _decision(
                "return_to_pm_l2",
                target_role="PM_L2_PHASE_OWNER",
                target_queue="browser_chat",
                handoff_required=True,
            )
        )
