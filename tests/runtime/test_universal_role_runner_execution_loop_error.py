from __future__ import annotations

from universal_role_runner import UniversalRoleRunner, build_role_task
from universal_role_runner.execution_loop import UniversalRoleRunnerExecutionLoop


CREATED_AT = "2026-06-27T00:00:00Z"


def _role_task(task_id: str = "role-task-loop-error") -> dict:
    return build_role_task(
        role_task_id=task_id,
        phase_run_id="phase-run-2f",
        lane="flowiseai_pm_orchestration",
        assigned_role="SUBCHAT_IMPLEMENTATION",
        approved_scope=["universal_role_runner/execution_loop.py"],
        forbidden_scope=["state_api/runtime/**", "contracts/schemas/**", ".github/**", "requirements*.txt"],
        acceptance_criteria=["execution loop records a terminal state when handler errors"],
        created_at=CREATED_AT,
    )


def test_execution_loop_marks_task_failed_when_handler_errors(operations) -> None:
    runner = UniversalRoleRunner(operations)
    loop = UniversalRoleRunnerExecutionLoop(runner, claimant_role="SUBCHAT_IMPLEMENTATION", claimant_id="loop-worker")
    runner.create_role_task(_role_task(), idempotency_key="urr-loop-error-create")

    def handler(_task: dict) -> dict:
        raise RuntimeError("boom")

    result = loop.run_once(handler, idempotency_key_prefix="urr-loop-error")

    assert result["status"] == "failed"
    assert result["claimed"] is True
    assert result["task_id"] == "role-task-loop-error"
    assert result["error"]["type"] == "RuntimeError"
    assert result["failure_transition"]["to_state"] == "failed"
    assert runner.read_role_task("role-task-loop-error")["task"]["lifecycle_state"] == "failed"
    assert operations.repository.count_rows("role_outputs") == 0
