from __future__ import annotations

from dataclasses import dataclass
from typing import Any


_STORED_ERROR_STATUS_CODE_FALLBACKS = {
    "validation_error": 422,
    "not_found": 404,
    "conflict": 409,
    "lease_error": 409,
}


@dataclass(slots=True)
class StateApiError(Exception):
    """Base runtime error with a stable machine-readable code."""

    code: str
    message: str
    status_code: int = 400
    details: dict[str, Any] | None = None

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"


def replay_stored_state_api_error(error: dict[str, Any]) -> StateApiError:
    """Rebuild a stored idempotency failure without changing its semantics."""

    code = error.get("code")
    if not isinstance(code, str) or not code:
        code = "runtime_error"

    message = error.get("message")
    if not isinstance(message, str) or not message:
        message = "stored idempotency failure"

    details = error.get("details")
    if not isinstance(details, dict):
        details = {}

    raw_status_code = error.get("status_code")
    if isinstance(raw_status_code, int) and not isinstance(raw_status_code, bool) and 100 <= raw_status_code <= 599:
        status_code = raw_status_code
    else:
        # Older local/dev records did not store status_code; keep known runtime
        # error classes on their original HTTP semantics when replayed.
        status_code = _STORED_ERROR_STATUS_CODE_FALLBACKS.get(code, 400)

    return StateApiError(code, message, status_code, details)


class RuntimeValidationError(StateApiError):
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__("validation_error", message, 422, details)


class NotFoundError(StateApiError):
    def __init__(self, resource: str, resource_id: str) -> None:
        super().__init__(
            "not_found",
            f"{resource} not found: {resource_id}",
            404,
            {"resource": resource, "resource_id": resource_id},
        )


class ConflictError(StateApiError):
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__("conflict", message, 409, details)


class IdempotencyConflictError(ConflictError):
    def __init__(self, operation_name: str, idempotency_key: str) -> None:
        super().__init__(
            "idempotency key was already used for a different request",
            {
                "operation_name": operation_name,
                "idempotency_key": idempotency_key,
            },
        )


class LeaseError(StateApiError):
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__("lease_error", message, 409, details)
