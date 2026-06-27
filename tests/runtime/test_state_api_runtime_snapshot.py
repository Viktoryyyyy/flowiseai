from __future__ import annotations

from conftest import sample_task


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
