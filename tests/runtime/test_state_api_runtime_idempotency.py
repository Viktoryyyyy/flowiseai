from __future__ import annotations

import pytest

from state_api.runtime.errors import IdempotencyConflictError, RuntimeValidationError

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


def test_same_operation_key_with_different_hash_conflicts(operations) -> None:
    operations.create_task(sample_task("task-conflict-a"), idempotency_key="idem-conflict")
    with pytest.raises(IdempotencyConflictError):
        operations.create_task(sample_task("task-conflict-b"), idempotency_key="idem-conflict")
