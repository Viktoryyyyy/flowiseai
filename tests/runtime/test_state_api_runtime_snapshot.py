from __future__ import annotations

from conftest import sample_audit_event, sample_handoff, sample_role_output, sample_task


def _out_of_scope(payload: dict, *, task_id: str) -> dict:
    out = dict(payload)
    out["project"] = "Other Project"
    out["lane"] = "other_lane"
    out["execution_mode"] = "other_mode"
    out["task_id"] = task_id
    return out


def test_state_snapshot_is_read_only_projection(operations) -> None:
    operations.create_task(sample_task("task-snapshot"), idempotency_key="idem-snapshot-create")
    audit_count_before = operations.repository.count_rows("audit_events")
    task_count_before = operations.repository.count_rows("tasks")

    first = operations.read_state_snapshot(
        project="MOEX Bot",
        lane="flowiseai_pm_orchestration",
        execution_mode="browser_chatgpt_github_direct",
    )
    second = operations.read_state_snapshot(
        project="MOEX Bot",
        lane="flowiseai_pm_orchestration",
        execution_mode="browser_chatgpt_github_direct",
    )

    assert first["state_snapshot"]["read_only"] is True
    assert first["state_snapshot"]["runtime_claim"] is False
    assert "task-snapshot" in first["state_snapshot"]["task_summary"]["task_refs"]
    assert second["state_snapshot"]["task_summary"] == first["state_snapshot"]["task_summary"]
    assert operations.repository.count_rows("audit_events") == audit_count_before
    assert operations.repository.count_rows("tasks") == task_count_before


def test_default_state_snapshot_scope_filters_repository_queries(operations) -> None:
    default_task_id = "task-default-scope"
    other_task_id = "task-other-scope"
    other_project = "Other Project"
    other_lane = "other_lane"
    other_execution_mode = "other_mode"

    operations.create_task(sample_task(default_task_id), idempotency_key="idem-default-scope-task")

    other_task = sample_task(other_task_id)
    other_task["project"] = other_project
    other_task["lane"] = other_lane
    other_task["execution_mode"] = other_execution_mode
    operations.create_task(other_task, idempotency_key="idem-other-scope-task")

    operations.persist_handoff(
        sample_handoff("handoff-default-scope", default_task_id),
        idempotency_key="idem-default-scope-handoff",
    )
    operations.persist_handoff(
        _out_of_scope(sample_handoff("handoff-other-scope", other_task_id), task_id=other_task_id),
        idempotency_key="idem-other-scope-handoff",
    )

    operations.persist_role_output(
        sample_role_output("role-output-default-scope", default_task_id),
        idempotency_key="idem-default-scope-role-output",
    )
    operations.persist_role_output(
        _out_of_scope(sample_role_output("role-output-other-scope", other_task_id), task_id=other_task_id),
        idempotency_key="idem-other-scope-role-output",
    )

    operations.append_audit_event(
        sample_audit_event("audit-default-scope", default_task_id),
        idempotency_key="idem-default-scope-audit",
    )
    operations.append_audit_event(
        _out_of_scope(sample_audit_event("audit-other-scope", other_task_id), task_id=other_task_id),
        idempotency_key="idem-other-scope-audit",
    )

    default_claim = operations.claim_next_task(
        lane="flowiseai_pm_orchestration",
        claimant_role="SUBCHAT_IMPLEMENTATION",
        claimant_id="worker-default",
        idempotency_key="idem-default-scope-claim",
    )
    other_claim = operations.claim_next_task(
        lane=other_lane,
        claimant_role="SUBCHAT_IMPLEMENTATION",
        claimant_id="worker-other",
        idempotency_key="idem-other-scope-claim",
    )
    default_lease_id = default_claim["lease"]["lease_id"]
    other_lease_id = other_claim["lease"]["lease_id"]

    default_snapshot = operations.read_state_snapshot()["state_snapshot"]

    assert default_snapshot["project"] == "MOEX Bot"
    assert default_snapshot["lane"] == "flowiseai_pm_orchestration"
    assert default_snapshot["execution_mode"] == "browser_chatgpt_github_direct"
    assert default_snapshot["task_summary"]["task_refs"] == [default_task_id]
    assert default_snapshot["task_summary"]["total_by_state"]["created"] == 1
    assert "handoff-default-scope" in default_snapshot["handoff_summary"]["handoff_refs"]
    assert "handoff-other-scope" not in default_snapshot["handoff_summary"]["handoff_refs"]
    assert "role-output-default-scope" in default_snapshot["role_output_summary"]["role_output_refs"]
    assert "role-output-other-scope" not in default_snapshot["role_output_summary"]["role_output_refs"]
    assert "audit-default-scope" in default_snapshot["audit_event_summary"]["audit_event_refs"]
    assert "audit-other-scope" not in default_snapshot["audit_event_summary"]["audit_event_refs"]
    assert default_lease_id in default_snapshot["lease_summary"]["active_lease_refs"]
    assert other_lease_id not in default_snapshot["lease_summary"]["active_lease_refs"]

    other_snapshot = operations.read_state_snapshot(
        project=other_project,
        lane=other_lane,
        execution_mode=other_execution_mode,
    )["state_snapshot"]
    assert other_snapshot["task_summary"]["task_refs"] == [other_task_id]
    assert other_lease_id in other_snapshot["lease_summary"]["active_lease_refs"]
    assert default_lease_id not in other_snapshot["lease_summary"]["active_lease_refs"]
