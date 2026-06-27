from __future__ import annotations

import pytest

from state_api.runtime.errors import IdempotencyConflictError, RuntimeValidationError, StateApiError

from conftest import sample_task


def test_mutating_operations_require_idempotency_key(operations) -> None:
    with pytest.raises(RuntimeValidationError):
        operations.create_task(sample_task("task-no-idem"), idempotency_key=None)


def test_same_operation_key_and_hash_replays_original_outcome(operations) -> None:
    task = sample_task("task-idem")
    first = operations.create_task(task, idempotency_key="idem-replay")
    second = operations.create_task(task, idempotency_key="idem-replay")
    assert second == first
    assert operations.repository.count_rows("tasks") == 1


def test_failed_duplicate_create_task_replays_original_error_semantics(operations) -> None:
    task = sample_task("task-failed-replay")
    operations.create_task(task, idempotency_key="idem-failed-replay-seed")

    with pytest.raises(StateApiError) as first_error:
        operations.create_task(task, idempotency_key="idem-failed-replay")

    assert first_error.value.code == "conflict"
    assert first_error.value.message == "task already exists"
    assert first_error.value.status_code == 409
    assert first_error.value.details == {"task_id": "task-failed-replay"}

    with pytest.raises(StateApiError) as replay_error:
        operations.create_task(task, idempotency_key="idem-failed-replay")

    assert replay_error.value.code == first_error.value.code
    assert replay_error.value.message == first_error.value.message
    assert replay_error.value.status_code == first_error.value.status_code
    assert replay_error.value.details == first_error.value.details
    assert not isinstance(replay_error.value, RuntimeValidationError)


def test_same_operation_key_with_different_hash_conflicts(operations) -> None:
    operations.create_task(sample_task("task-conflict-a"), idempotency_key="idem-conflict")
    with pytest.raises(IdempotencyConflictError):
        operations.create_task(sample_task("task-conflict-b"), idempotency_key="idem-conflict")
