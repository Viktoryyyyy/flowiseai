from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class StateApiError(Exception):
    """Base runtime error with a stable machine-readable code."""

    code: str
    message: str
    status_code: int = 400
    details: dict[str, Any] | None = None

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"


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
