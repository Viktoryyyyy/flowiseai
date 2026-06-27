from __future__ import annotations

from universal_role_runner import UniversalRoleRunner, build_role_output, build_role_task


CREATED_AT = "2026-06-27T00:00:00Z"


def _role_task(task_id: str) -> dict:
    return build_role_task(
        role_task_id=task_id,
        phase_run_id="phase-run-2e",
        lane="flowiseai_pm_orchestration",
        assigned_role="SUBCHAT_IMPLEMENTATION",
        approved_scope=["universal_role_runner/**"],
        forbidden_scope=["state_api/runtime/**", "contracts/schemas/**"],
        acceptance_criteria=["idempotent replay is deterministic"],
        created_at=CREATED_AT,
    )


def _decision() -> dict:
    return {
        "contract_version": "1.0.0",
        "decision_id": "decision-idempotent",
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
            "criteria_met": ["idempotency verified"],
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


def test_create_role_task_replays_with_same_idempotency_key(operations) -> None:
    runner = UniversalRoleRunner(operations)
    task = _role_task("role-task-idempotent")

    first = runner.create_role_task(task, idempotency_key="urr-idem-create")
    second = runner.create_role_task(task, idempotency_key="urr-idem-create")

    assert second == first
    assert operations.repository.count_rows("tasks") == 1


def test_role_output_persistence_replays_with_same_idempotency_key(operations) -> None:
    runner = UniversalRoleRunner(operations)
    runner.create_role_task(_role_task("role-task-output-idem"), idempotency_key="urr-output-task-create")

    role_output = build_role_output(
        role_output_id="role-output-idempotent",
        role_task_id="role-task-output-idem",
        producing_role="SUBCHAT_IMPLEMENTATION",
        output_type="implementation_report",
        payload={"status": "pass"},
        created_at=CREATED_AT,
    )

    first = runner.persist_role_output(role_output, idempotency_key="urr-output-persist")
    second = runner.persist_role_output(role_output, idempotency_key="urr-output-persist")

    assert second == first
    assert operations.repository.count_rows("role_outputs") == 1


def test_pm_l3_decision_persistence_replays_with_same_idempotency_key(operations) -> None:
    runner = UniversalRoleRunner(operations)
    runner.create_role_task(_role_task("role-task-decision-idem"), idempotency_key="urr-decision-task-create")

    first = runner.persist_pm_l3_decision(
        _decision(),
        role_task_id="role-task-decision-idem",
        role_output_id="role-output-decision-idem",
        created_at=CREATED_AT,
        idempotency_key="urr-decision-persist",
    )
    second = runner.persist_pm_l3_decision(
        _decision(),
        role_task_id="role-task-decision-idem",
        role_output_id="role-output-decision-idem",
        created_at=CREATED_AT,
        idempotency_key="urr-decision-persist",
    )

    assert second == first
    assert operations.repository.count_rows("role_outputs") == 1
