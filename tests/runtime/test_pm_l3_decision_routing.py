from __future__ import annotations

import pytest

from universal_role_runner.decision_routing import PMDecisionRoutingError, route_pm_l3_decision


CREATED_AT = "2026-06-27T00:00:00Z"


def _decision(decision_type: str, **overrides: object) -> dict:
    decision = {
        "contract_version": "1.0.0",
        "decision_id": f"decision-{decision_type}",
        "phase_run_id": "phase-run-3",
        "decision_type": decision_type,
        "next_role": None,
        "next_task": None,
        "routing_target": {"target_role": None, "target_queue": "none", "handoff_required": False},
        "acceptance_details": {"accepted": False, "criteria_met": []},
        "rejection_details": {"rejected": False, "reasons": []},
        "blocker_details": {"blocked": False, "blockers": []},
        "created_at": CREATED_AT,
    }
    decision.update(overrides)
    return decision


def test_route_next_role_produces_role_task_request_artifact() -> None:
    result = route_pm_l3_decision(
        _decision(
            "route_next_role",
            next_role="SUBCHAT_IMPLEMENTATION",
            next_task={"task_id": "phase-3a-implementation"},
            routing_target={
                "target_role": "SUBCHAT_IMPLEMENTATION",
                "target_queue": "browser_chat",
                "handoff_required": True,
            },
        )
    )

    assert result["routing_status"] == "routed"
    assert result["next_action"] == "create_or_persist_role_task"
    assert result["next_step_artifact"]["artifact_type"] == "role_task_request"
    assert result["next_step_artifact"]["side_effects"]["server_apply_executed"] is False


@pytest.mark.parametrize(
    ("decision_type", "expected_status", "expected_action", "artifact_type", "overrides"),
    [
        (
            "accept_role_output",
            "accepted",
            "record_decision",
            "role_output_acceptance",
            {"acceptance_details": {"accepted": True, "criteria_met": ["criteria met"]}},
        ),
        (
            "reject_role_output",
            "rejected",
            "record_decision",
            "role_output_rejection",
            {"rejection_details": {"rejected": True, "reasons": ["missing evidence"]}},
        ),
        (
            "raise_blocker",
            "blocked",
            "record_blocker_and_stop",
            "blocker_escalation",
            {
                "blocker_details": {
                    "blocked": True,
                    "blockers": [{"code": "blocked", "message": "blocked", "severity": "blocking"}],
                }
            },
        ),
        (
            "return_to_pm_l2",
            "returned_to_pm_l2",
            "generate_pm_l2_handoff",
            "pm_l2_return_package_request",
            {"routing_target": {"target_role": "PM_L2_PHASE_OWNER", "target_queue": "pm_l2_return", "handoff_required": True}},
        ),
        (
            "complete_phase_step",
            "phase_step_completed",
            "record_phase_step_completion",
            "phase_step_completion_record",
            {"acceptance_details": {"accepted": True, "criteria_met": ["step complete"]}},
        ),
    ],
)
def test_supported_decision_types_produce_deterministic_artifacts(
    decision_type: str,
    expected_status: str,
    expected_action: str,
    artifact_type: str,
    overrides: dict,
) -> None:
    result = route_pm_l3_decision(_decision(decision_type, **overrides))

    assert result["routing_status"] == expected_status
    assert result["next_action"] == expected_action
    assert result["next_step_artifact"]["artifact_type"] == artifact_type


def test_request_correction_routes_a_correction_task() -> None:
    result = route_pm_l3_decision(
        _decision(
            "request_correction",
            next_role="SUBCHAT_IMPLEMENTATION",
            next_task={"task_id": "correct-phase-3a-output"},
            routing_target={"target_role": "SUBCHAT_IMPLEMENTATION", "target_queue": "n8n_role_task_queue", "handoff_required": True},
            rejection_details={"rejected": True, "reasons": ["validation failed"]},
        )
    )

    assert result["routing_status"] == "correction_requested"
    assert result["next_action"] == "route_correction_task"


def test_route_next_role_rejects_missing_next_task() -> None:
    with pytest.raises(PMDecisionRoutingError):
        route_pm_l3_decision(
            _decision(
                "route_next_role",
                next_role="SUBCHAT_IMPLEMENTATION",
                routing_target={"target_role": "SUBCHAT_IMPLEMENTATION", "target_queue": "browser_chat", "handoff_required": True},
            )
        )
