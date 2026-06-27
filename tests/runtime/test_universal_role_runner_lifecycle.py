from __future__ import annotations

from universal_role_runner import UniversalRoleRunner, build_role_output, build_role_task


CREATED_AT = "2026-06-27T00:00:00Z"


def _role_task(task_id: str = "role-task-lifecycle") -> dict:
    return build_role_task(
        role_task_id=task_id,
        phase_run_id="phase-run-2e",
        lane="flowiseai_pm_orchestration",
        assigned_role="SUBCHAT_IMPLEMENTATION",
        approved_scope=["universal_role_runner/**", "tests/runtime/test_universal_role_runner_lifecycle.py"],
        forbidden_scope=["state_api/runtime/**", "contracts/schemas/**", ".github/**", "requirements*.txt"],
        acceptance_criteria=["local/dev lifecycle uses StateApiOperations public methods"],
        created_at=CREATED_AT,
    )


def test_runner_lifecycle_uses_state_api_public_operations(operations) -> None:
    runner = UniversalRoleRunner(operations)
    role_task = _role_task()

    created = runner.create_role_task(role_task, idempotency_key="urr-lifecycle-create")
    assert created["task_ref"] == "role-task-lifecycle"
    assert created["task"]["task_id"] == "role-task-lifecycle"
    assert created["task"]["role_task_id"] == "role-task-lifecycle"

    read_back = runner.read_role_task("role-task-lifecycle")
    assert read_back["task"]["project"] == "MOEX Bot"

    claim = runner.claim_next_role_task(
        lane="flowiseai_pm_orchestration",
        claimant_role="SUBCHAT_IMPLEMENTATION",
        claimant_id="worker-phase-2e",
        idempotency_key="urr-lifecycle-claim",
    )
    lease = claim["lease"]
    assert lease["task_id"] == "role-task-lifecycle"
    assert lease["claimant_role"] == "SUBCHAT_IMPLEMENTATION"
    assert lease["claimant_id"] == "worker-phase-2e"

    assigned = runner.transition_role_task(
        "role-task-lifecycle",
        "assigned",
        idempotency_key="urr-lifecycle-assigned",
        actor_role="SUBCHAT_IMPLEMENTATION",
        reason="claimed by local/dev runner",
    )
    assert assigned["state_transition"]["from_state"] == "created"
    assert assigned["state_transition"]["to_state"] == "assigned"

    running = runner.transition_role_task(
        "role-task-lifecycle",
        "running",
        idempotency_key="urr-lifecycle-running",
        actor_role="SUBCHAT_IMPLEMENTATION",
        reason="begin local/dev task",
    )
    assert running["state_transition"]["from_state"] == "assigned"
    assert running["state_transition"]["to_state"] == "running"

    role_output = build_role_output(
        role_output_id="role-output-lifecycle",
        role_task_id="role-task-lifecycle",
        producing_role="SUBCHAT_IMPLEMENTATION",
        output_type="implementation_report",
        payload={"status": "pass"},
        created_at=CREATED_AT,
    )
    persisted = runner.persist_role_output(role_output, idempotency_key="urr-lifecycle-output")
    assert persisted["role_output_ref"] == "role-output-lifecycle"
    assert persisted["role_output"]["task_id"] == "role-task-lifecycle"
    assert persisted["role_output"]["structured_payload"]["output_type"] == "implementation_report"


def test_persist_role_output_defaults_scope_for_contract_payload_without_metadata(operations) -> None:
    runner = UniversalRoleRunner(operations)
    runner.create_role_task(_role_task("role-task-raw-output"), idempotency_key="urr-raw-output-create")
    role_output = build_role_output(
        role_output_id="role-output-raw-contract",
        role_task_id="role-task-raw-output",
        producing_role="SUBCHAT_IMPLEMENTATION",
        output_type="implementation_report",
        payload={"status": "pass"},
        created_at=CREATED_AT,
    )
    role_output.pop("metadata")

    persisted = runner.persist_role_output(role_output, idempotency_key="urr-raw-output-persist")

    assert persisted["role_output"]["lane"] == "flowiseai_pm_orchestration"
    assert persisted["role_output"]["execution_mode"] == "browser_chatgpt_github_direct"


def test_claim_lease_blocks_second_claim_until_release(operations) -> None:
    runner = UniversalRoleRunner(operations)
    runner.create_role_task(_role_task("role-task-lease"), idempotency_key="urr-lease-create")

    first = runner.claim_next_role_task(
        lane="flowiseai_pm_orchestration",
        claimant_role="SUBCHAT_IMPLEMENTATION",
        claimant_id="worker-a",
        idempotency_key="urr-lease-claim-a",
    )
    assert first["lease"]["task_id"] == "role-task-lease"

    second = runner.claim_next_role_task(
        lane="flowiseai_pm_orchestration",
        claimant_role="SUBCHAT_IMPLEMENTATION",
        claimant_id="worker-b",
        idempotency_key="urr-lease-claim-b",
    )
    assert second["lease"] is None