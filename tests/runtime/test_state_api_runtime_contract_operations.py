from __future__ import annotations

from state_api.runtime.app import create_app
from state_api.runtime.models import REQUIRED_OPERATIONS
from state_api.runtime.operations import StateApiOperations

from conftest import sample_audit_event, sample_handoff, sample_role_output, sample_task


def test_fastapi_style_asgi_app_object_exists() -> None:
    app = create_app()
    try:
        assert callable(app)
        assert hasattr(app, "router")
        assert hasattr(app.state, "operations")
    finally:
        app.state.repository.close()


def test_all_required_operations_are_exposed(operations: StateApiOperations) -> None:
    for operation_name in REQUIRED_OPERATIONS:
        assert hasattr(operations, operation_name)


def test_required_operations_execute_minimal_happy_path(operations: StateApiOperations) -> None:
    created = operations.create_task(sample_task("task-ops"), idempotency_key="idem-create-ops")
    assert created["task_ref"] == "task-ops"

    read = operations.read_task("task-ops")
    assert read["task"]["task_id"] == "task-ops"

    transitioned = operations.transition_task_state(
        "task-ops",
        "assigned",
        actor_role="SUBCHAT_IMPLEMENTATION",
        reason="ready for claim",
        idempotency_key="idem-transition-ops",
    )
    assert transitioned["state_transition"]["to_state"] == "assigned"

    claim = operations.claim_next_task(
        lane="flowiseai_pm_orchestration",
        claimant_role="SUBCHAT_IMPLEMENTATION",
        claimant_id="worker-1",
        idempotency_key="idem-claim-ops",
    )
    assert claim["lease"]["task_id"] == "task-ops"

    renewed = operations.renew_task_lease(
        claim["lease"]["lease_id"],
        claimant_id="worker-1",
        idempotency_key="idem-renew-ops",
    )
    assert renewed["lease"]["lease_state"] == "renewed"

    released = operations.release_task_lease(
        claim["lease"]["lease_id"],
        claimant_id="worker-1",
        idempotency_key="idem-release-ops",
    )
    assert released["lease"]["lease_state"] == "released"

    handoff = operations.persist_handoff(sample_handoff("handoff-ops", "task-ops"), idempotency_key="idem-handoff-ops")
    assert handoff["handoff_ref"] == "handoff-ops"

    role_output = operations.persist_role_output(
        sample_role_output("role-output-ops", "task-ops"),
        idempotency_key="idem-role-output-ops",
    )
    assert role_output["role_output_ref"] == "role-output-ops"

    audit = operations.append_audit_event(sample_audit_event("audit-ops", "task-ops"), idempotency_key="idem-audit-ops")
    assert audit["audit_event_ref"] == "audit-ops"

    snapshot = operations.read_state_snapshot(
        project="MOEX Bot",
        lane="flowiseai_pm_orchestration",
        execution_mode="browser_chatgpt_github_direct",
    )
    assert "state_snapshot" in snapshot
    assert "task-ops" in snapshot["state_snapshot"]["task_summary"]["task_refs"]
