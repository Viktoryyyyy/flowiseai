from __future__ import annotations

from dataclasses import dataclass
from typing import Any


JsonDict = dict[str, Any]

CONTRACT_VERSION = "1.0.0"
PROJECT_NAME = "MOEX Bot"

EXECUTION_MODES = {
    "browser_chatgpt_github_direct",
    "route_b_n8n_universal_role_runner",
}

ROLE_TASK_STATUSES = {
    "created",
    "assigned",
    "claimed",
    "in_progress",
    "output_submitted",
    "validated",
    "blocked",
    "failed",
    "cancelled",
}

ROLE_OUTPUT_TYPES = {
    "handoff_intake",
    "implementation_report",
    "validation_report",
    "blocker_report",
    "decision_report",
    "evidence_report",
}

PM_L3_DECISION_TYPES = {
    "route_next_role",
    "accept_role_output",
    "reject_role_output",
    "request_correction",
    "raise_blocker",
    "complete_phase_step",
    "return_to_pm_l2",
}

GITHUB_REQUEST_OPERATION_TYPES = {
    "create_branch",
    "commit_approved_scope",
    "open_pull_request",
    "verify_ci",
    "update_pull_request_metadata",
}

GITHUB_REQUEST_CONCLUSIONS = {
    "not_started",
    "pending",
    "success",
    "failure",
    "cancelled",
    "skipped",
    "not_required",
}


class UniversalRoleRunnerError(ValueError):
    """Base local/dev Universal Role Runner error."""


class SchemaValidationError(UniversalRoleRunnerError):
    """Raised when a Phase 2E local validator rejects a payload."""

    def __init__(self, message: str, details: JsonDict | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class BoundaryViolationError(UniversalRoleRunnerError):
    """Raised when a caller asks the local/dev runner to execute forbidden work."""

    def __init__(self, message: str, details: JsonDict | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


@dataclass(frozen=True, slots=True)
class IdempotencyKeys:
    create_task: str
    claim_task: str
    transition_task: str
    persist_role_output: str
    persist_decision: str
    persist_github_execution_request: str


def require_idempotency_key(value: str | None, operation_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise SchemaValidationError(
            "idempotency key is required",
            {"operation_name": operation_name},
        )
    return value
