from __future__ import annotations

from universal_role_runner import UniversalRoleRunner, build_role_output, build_role_task
from universal_role_runner.execution_loop import UniversalRoleRunnerExecutionLoop


CREATED_AT = "2026-06-27T00:00:00Z"


def _role_task(task_id: str = "role-task-loop") -> dict:
    return build_role_task(
        role_task_id=task_id,
        phase_run_id="phase-run-2f",
        lane="flowiseai_pm_orchestration",
        assigned_role="SUBCHAT_IMPLEMENTATION",
        approved_scope=["universal_role_runner/execution_loop.py"],
        forbidden_scope=["state_api/runtime/**", "contracts/schemas/**", ".github/**", "requirements*.txt"],
        acceptance_criteria=["execution loop claims one task and persists one output"],
        created_at=CREATED_AT,
    )


def _role_output(task_id: str, output_id: str = "role-output-loop") -> dict:
    return build_role_output(
        role_output_id=output_id,
        role_task_id=task_id,
        producing_role="SUBCHAT_IMPLEMENTATION",
        output_type="implementation_report",
        payload={"status": "pass"},
        created_at=CREATED_AT,
    )


def test_execution_loop_returns_idle_when_queue_is_empty(operations) -> None:
    runner = UniversalRoleRunner(operations)
    loop = UniversalRoleRunnerExecutionLoop(runner)

    result = loop.run_once(lambda task: _role_output(str(task["task_id"])), idempotency_key_prefix="urr-loop-idle")

    assert result["status"] == "idle"
    assert result["claimed"] is False
    assert result["task_id"] is None
    assert result["role_output_ref"] is None


def test_execution_loop_claims_runs_persists_output_and_completes_task(operations) -> None:
    runner = UniversalRoleRunner(operations)
    loop = UniversalRoleRunnerExecutionLoop(
        runner,
        claimant_role="SUBCHAT_IMPLEMENTATION",
        claimant_id="loop-worker",
    )
    runner.create_role_task(_role_task(), idempotency_key="urr-loop-create")

    result = loop.run_once(
        lambda task: _role_output(str(task["task_id"])),
        idempotency_key_prefix="urr-loop-success",
    )

    assert result["status"] == "completed"
    assert result["claimed"] is True
    assert result["task_id"] == "role-task-loop"
    assert result["role_output_ref"] == "role-output-loop"
    assert result["assigned_transition"]["to_state"] == "assigned"
    assert result["running_transition"]["to_state"] == "running"
    assert result["completed_transition"]["to_state"] == "completed"

    task = runner.read_role_task("role-task-loop")["task"]
    assert task["lifecycle_state"] == "completed"
    assert operations.repository.count_rows("role_outputs") == 1
