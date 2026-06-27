from __future__ import annotations

import uuid

from .models import STATE_API_SCHEMA_VERSION, JsonDict
from .persistence import SQLiteStateRepository


def build_state_snapshot(
    *,
    repository: SQLiteStateRepository,
    generated_at: str,
    project: str | None = None,
    lane: str | None = None,
    execution_mode: str | None = None,
) -> JsonDict:
    resolved_project = project or "MOEX Bot"
    resolved_lane = lane or "flowiseai_pm_orchestration"
    resolved_execution_mode = execution_mode or "browser_chatgpt_github_direct"

    return {
        "snapshot_id": f"snapshot-{uuid.uuid4()}",
        "schema_version": STATE_API_SCHEMA_VERSION,
        "project": resolved_project,
        "lane": resolved_lane,
        "execution_mode": resolved_execution_mode,
        "generated_at": generated_at,
        "read_only": True,
        "runtime_claim": False,
        "task_summary": {
            "task_refs": repository.refs_for_table("tasks", "task_id", project, lane, execution_mode),
            "total_by_state": repository.task_state_counts(project, lane, execution_mode),
        },
        "handoff_summary": {
            "handoff_refs": repository.refs_for_table("handoffs", "handoff_id", project, lane, execution_mode),
        },
        "role_output_summary": {
            "role_output_refs": repository.refs_for_table("role_outputs", "role_output_id", project, lane, execution_mode),
        },
        "audit_event_summary": {
            "audit_event_refs": repository.refs_for_table("audit_events", "event_id", project, lane, execution_mode),
            "append_only": True,
        },
        "lease_summary": {
            "active_lease_refs": repository.active_lease_refs(project, lane, execution_mode, generated_at),
        },
    }
