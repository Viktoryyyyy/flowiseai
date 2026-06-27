from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

JsonDict = dict[str, Any]

STATE_API_SCHEMA_VERSION = "1.0.0"
PROJECT_NAME = "MOEX Bot"
DEFAULT_LEASE_DURATION_SECONDS = 600
MAX_LEASE_DURATION_SECONDS = 3600
DEFAULT_MAX_ATTEMPTS = 3
DEFAULT_BACKOFF_SECONDS = 60

LifecycleState = Literal[
    "created",
    "assigned",
    "running",
    "blocked",
    "completed",
    "validation_pending",
    "validated",
    "failed",
]

LIFECYCLE_STATES: tuple[str, ...] = (
    "created",
    "assigned",
    "running",
    "blocked",
    "completed",
    "validation_pending",
    "validated",
    "failed",
)

ALLOWED_TRANSITIONS: dict[str, list[str]] = {
    "created": ["assigned", "blocked", "failed"],
    "assigned": ["running", "blocked", "failed"],
    "running": ["assigned", "blocked", "completed", "validation_pending", "failed"],
    "blocked": ["assigned", "failed"],
    "completed": ["validation_pending", "validated"],
    "validation_pending": ["validated", "blocked", "failed"],
    "validated": [],
    "failed": [],
}

TERMINAL_STATES: tuple[str, ...] = ("validated", "failed")

REQUIRED_OPERATIONS: tuple[str, ...] = (
    "create_task",
    "read_task",
    "transition_task_state",
    "claim_next_task",
    "renew_task_lease",
    "release_task_lease",
    "persist_handoff",
    "persist_role_output",
    "append_audit_event",
    "read_state_snapshot",
)

MUTATING_OPERATIONS: tuple[str, ...] = (
    "create_task",
    "transition_task_state",
    "claim_next_task",
    "renew_task_lease",
    "release_task_lease",
    "persist_handoff",
    "persist_role_output",
    "append_audit_event",
)


@dataclass(frozen=True, slots=True)
class IdempotencyOutcome:
    replayed: bool
    result: JsonDict
