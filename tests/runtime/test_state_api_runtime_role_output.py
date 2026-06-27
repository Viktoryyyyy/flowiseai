from __future__ import annotations

import pytest

from state_api.runtime.errors import ConflictError

from conftest import sample_role_output


def test_role_output_is_immutable_after_creation(operations) -> None:
    original = sample_role_output("role-output-immutable", "task-role-output")
    first = operations.persist_role_output(original, idempotency_key="idem-role-output-original")
    assert first["role_output_ref"] == "role-output-immutable"

    changed = sample_role_output("role-output-immutable", "task-role-output")
    changed["payload"] = {"result": "changed"}
    with pytest.raises(ConflictError):
        operations.persist_role_output(changed, idempotency_key="idem-role-output-conflict")


def test_role_output_correction_uses_new_record(operations) -> None:
    operations.persist_role_output(
        sample_role_output("role-output-v1", "task-role-output-v2"),
        idempotency_key="idem-role-output-v1",
    )
    correction = operations.persist_role_output(
        sample_role_output("role-output-v2", "task-role-output-v2"),
        idempotency_key="idem-role-output-v2",
    )
    assert correction["role_output_ref"] == "role-output-v2"
    assert operations.repository.count_rows("role_outputs") == 2
