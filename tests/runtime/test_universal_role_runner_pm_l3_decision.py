from __future__ import annotations

from universal_role_runner import UniversalRoleRunner, build_role_task


CREATED_AT = "2026-06-27T00:00:00Z"


def _role_task() -> dict:
    return build_role_task(
        role_task_id="role-task-pm-l3-decision",
        phase_run_id="phase-run-2e",
        lane="flowiseai_pm_orchestration",
        assigned_role="PM_L3_DELIVERY_VALIDATION_OWNER",
        approved_scope=["universal_role_runner/**"],
        forbidden_scope=["state_api/runtime/**", "contracts/schemas/**"],
        acceptance_criteria=["PM L3 decision is persisted as decision_report RoleOutput"],
        created_at=CREATED_AT,
    )


def _decision() -> dict:
    return {
        "contract_version": "1.0.0",
        "decision_id": "decision-pm-l3",
        "phase_run_id": "phase-run-2e",
        "decision_type": "route_next_role",
        "next_role": "SUBCHAT_VALIDATION",
        "next_task": {
            "task_id": "flowiseai_phase_2e_validation",
            "goal": "Validate Phase 2E implementation evidence",
        },
        "routing_target": {
            "target_role": "SUBCHAT_VALIDATION",
            "target_queue": "browser_chat",
            "handoff_required": True,
        },
        "acceptance_details": {
            "accepted": False,
            "criteria_met": [],
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


def test_pm_l3_decision_persists_as_decision_report_role_output(operations) -> None:
    runner = UniversalRoleRunner(operations)
    runner.create_role_task(_role_task(), idempotency_key="urr-pm-l3-task-create")

    persisted = runner.persist_pm_l3_decision(
        _decision(),
        role_task_id="role-task-pm-l3-decision",
        role_output_id="role-output-pm-l3-decision",
        created_at=CREATED_AT,
        idempotency_key="urr-pm-l3-decision-persist",
    )

    assert persisted["role_output_ref"] == "role-output-pm-l3-decision"
    role_output = persisted["role_output"]
    assert role_output["task_id"] == "role-task-pm-l3-decision"
    assert role_output["role"] == "PM_L3_DELIVERY_VALIDATION_OWNER"
    assert role_output["structured_payload"]["output_type"] == "decision_report"
    assert role_output["structured_payload"]["payload"]["decision_id"] == "decision-pm-l3"
    assert role_output["structured_payload"]["payload"]["routing_target"]["target_role"] == "SUBCHAT_VALIDATION"
