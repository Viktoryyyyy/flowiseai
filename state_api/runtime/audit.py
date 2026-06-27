from __future__ import annotations

import uuid
from typing import Any

from .models import STATE_API_SCHEMA_VERSION, JsonDict


def build_audit_event(
    *,
    task: JsonDict | None,
    operation_name: str,
    event_type: str,
    actor_role: str,
    occurred_at: str,
    outcome: str,
    subject_ref: JsonDict | None = None,
    evidence_ref: JsonDict | None = None,
    state_transition: JsonDict | None = None,
    idempotency_key: str | None = None,
    lease_ref: str | None = None,
) -> JsonDict:
    source = task or {}
    event: JsonDict = {
        "event_id": f"audit-{uuid.uuid4()}",
        "schema_version": STATE_API_SCHEMA_VERSION,
        "occurred_at": occurred_at,
        "project": source.get("project", "MOEX Bot"),
        "task_id": source.get("task_id", "not_applicable"),
        "lane": source.get("lane", "flowiseai_pm_orchestration"),
        "execution_mode": source.get("execution_mode", "browser_chatgpt_github_direct"),
        "actor_role": actor_role,
        "event_type": event_type,
        "operation_name": operation_name,
        "subject_ref": subject_ref or {},
        "evidence_ref": evidence_ref or {},
        "outcome": outcome,
        "redaction_state": "no_secret_payload",
        "append_only": True,
    }
    if state_transition is not None:
        event["state_transition"] = state_transition
    if idempotency_key is not None:
        event["idempotency_key"] = idempotency_key
    if lease_ref is not None:
        event["lease_ref"] = lease_ref
    return event
