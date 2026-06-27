from __future__ import annotations

import copy
import hashlib
import json
from typing import Callable

from .errors import (
    IdempotencyConflictError,
    RuntimeValidationError,
    StateApiError,
    replay_stored_state_api_error,
)
from .models import JsonDict
from .persistence import SQLiteStateRepository
from .validation import require_idempotency_key


def request_identity_hash(operation_name: str, request_payload: JsonDict) -> str:
    canonical_payload = json.dumps(
        {"operation_name": operation_name, "request": request_payload},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical_payload.encode("utf-8")).hexdigest()


def extract_task_id(request_payload: JsonDict, result: JsonDict | None = None) -> str:
    for source in (result or {}, request_payload):
        if isinstance(source.get("task_id"), str) and source["task_id"]:
            return source["task_id"]
        task = source.get("task")
        if isinstance(task, dict) and isinstance(task.get("task_id"), str) and task["task_id"]:
            return task["task_id"]
        lease = source.get("lease")
        if isinstance(lease, dict) and isinstance(lease.get("task_id"), str) and lease["task_id"]:
            return lease["task_id"]
        handoff = source.get("handoff")
        if isinstance(handoff, dict) and isinstance(handoff.get("task_id"), str) and handoff["task_id"]:
            return handoff["task_id"]
        role_output = source.get("role_output")
        if isinstance(role_output, dict) and isinstance(role_output.get("task_id"), str) and role_output["task_id"]:
            return role_output["task_id"]
        audit_event = source.get("audit_event")
        if isinstance(audit_event, dict) and isinstance(audit_event.get("task_id"), str) and audit_event["task_id"]:
            return audit_event["task_id"]
    return "not_applicable"


def execute_idempotent(
    *,
    repository: SQLiteStateRepository,
    operation_name: str,
    idempotency_key: str | None,
    request_payload: JsonDict,
    now_iso: str,
    action: Callable[[], JsonDict],
) -> JsonDict:
    key = require_idempotency_key(operation_name, idempotency_key)
    request_payload_copy = copy.deepcopy(request_payload)
    identity_hash = request_identity_hash(operation_name, request_payload_copy)
    existing = repository.get_idempotency_record(operation_name, key)

    if existing is not None:
        if existing["request_identity_hash"] != identity_hash:
            raise IdempotencyConflictError(operation_name, key)
        if existing["status"] == "succeeded" and isinstance(existing.get("result"), dict):
            return copy.deepcopy(existing["result"])
        if existing["status"] == "failed" and isinstance(existing.get("error"), dict):
            raise replay_stored_state_api_error(existing["error"])
        raise RuntimeValidationError(
            "idempotency record has unsupported status",
            {"operation_name": operation_name, "idempotency_key": key, "status": existing.get("status")},
        )

    try:
        with repository.transaction():
            result = action()
            repository.insert_idempotency_record(
                operation_name=operation_name,
                idempotency_key=key,
                request_identity_hash=identity_hash,
                task_id=extract_task_id(request_payload_copy, result),
                status="succeeded",
                result=copy.deepcopy(result),
                error=None,
                now_iso=now_iso,
            )
            return result
    except StateApiError as exc:
        if repository.get_idempotency_record(operation_name, key) is None:
            with repository.transaction():
                repository.insert_idempotency_record(
                    operation_name=operation_name,
                    idempotency_key=key,
                    request_identity_hash=identity_hash,
                    task_id=extract_task_id(request_payload_copy),
                    status="failed",
                    result=None,
                    error={
                        "code": exc.code,
                        "message": exc.message,
                        "status_code": exc.status_code,
                        "details": exc.details or {},
                    },
                    now_iso=now_iso,
                )
        raise
