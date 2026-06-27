from __future__ import annotations

from typing import Any

from .errors import RuntimeValidationError
from .models import ALLOWED_TRANSITIONS, LIFECYCLE_STATES, MUTATING_OPERATIONS, TERMINAL_STATES


def require_idempotency_key(operation_name: str, idempotency_key: str | None) -> str:
    if operation_name in MUTATING_OPERATIONS and not idempotency_key:
        raise RuntimeValidationError(
            "mutating operations require an idempotency key",
            {"operation_name": operation_name},
        )
    assert idempotency_key is not None
    return idempotency_key


def validate_lifecycle_state(state: str) -> None:
    if state not in LIFECYCLE_STATES:
        raise RuntimeValidationError("unknown task lifecycle state", {"state": state})


def validate_transition(from_state: str, to_state: str) -> None:
    validate_lifecycle_state(from_state)
    validate_lifecycle_state(to_state)
    if from_state in TERMINAL_STATES:
        raise RuntimeValidationError(
            "terminal task states have no outgoing transitions",
            {"from_state": from_state, "to_state": to_state},
        )
    allowed_targets = ALLOWED_TRANSITIONS[from_state]
    if to_state not in allowed_targets:
        raise RuntimeValidationError(
            "task lifecycle transition is not allowed",
            {"from_state": from_state, "to_state": to_state, "allowed_targets": allowed_targets},
        )


def ensure_object(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise RuntimeValidationError(f"{field_name} must be an object")
    return value


def require_non_empty_string(payload: dict[str, Any], field_name: str) -> str:
    value = payload.get(field_name)
    if not isinstance(value, str) or not value:
        raise RuntimeValidationError(f"{field_name} is required", {"field_name": field_name})
    return value


def validate_lease_duration(
    lease_duration_seconds: int | None,
    default_duration_seconds: int,
    max_duration_seconds: int,
) -> int:
    duration = default_duration_seconds if lease_duration_seconds is None else lease_duration_seconds
    if not isinstance(duration, int) or duration <= 0:
        raise RuntimeValidationError(
            "lease duration must be a positive integer",
            {"lease_duration_seconds": lease_duration_seconds},
        )
    if duration > max_duration_seconds:
        raise RuntimeValidationError(
            "lease duration exceeds max lease duration",
            {
                "lease_duration_seconds": duration,
                "max_lease_duration_seconds": max_duration_seconds,
            },
        )
    return duration
