from __future__ import annotations

import sqlite3

import pytest

from conftest import sample_audit_event, sample_task


def test_mutations_append_audit_events(operations) -> None:
    operations.create_task(sample_task("task-audit"), idempotency_key="idem-audit-create")
    assert operations.repository.count_rows("audit_events") == 1

    operations.transition_task_state(
        "task-audit",
        "assigned",
        actor_role="SUBCHAT_IMPLEMENTATION",
        idempotency_key="idem-audit-transition",
    )
    assert operations.repository.count_rows("audit_events") == 2


def test_append_audit_event_is_append_only(operations) -> None:
    operations.append_audit_event(sample_audit_event("audit-append-only"), idempotency_key="idem-append-only")
    assert operations.repository.count_rows("audit_events") == 1

    with pytest.raises(sqlite3.DatabaseError):
        operations.repository._connection.execute(
            "UPDATE audit_events SET payload_json = ? WHERE event_id = ?",
            ("{}", "audit-append-only"),
        )

    with pytest.raises(sqlite3.DatabaseError):
        operations.repository._connection.execute(
            "DELETE FROM audit_events WHERE event_id = ?",
            ("audit-append-only",),
        )
