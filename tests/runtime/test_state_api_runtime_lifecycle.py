from __future__ import annotations

import pytest

from state_api.runtime.errors import RuntimeValidationError
from state_api.runtime.models import ALLOWED_TRANSITIONS, TERMINAL_STATES

from conftest import sample_task


def test_valid_lifecycle_transition_is_enforced(operations) -> None:
    operations.create_task(sample_task("task-life"), idempotency_key="idem-life-create")
    result = operations.transition_task_state(
        "task-life",
        "assigned",
        actor_role="SUBCHAT_IMPLEMENTATION",
        idempotency_key="idem-life-transition",
    )
    assert result["state_transition"]["from_state"] == "created"
    assert result["state_transition"]["to_state"] == "assigned"
    assert result["state_transition"]["allowed_transitions"] == ALLOWED_TRANSITIONS


def test_invalid_lifecycle_transition_is_rejected(operations) -> None:
    operations.create_task(sample_task("task-invalid"), idempotency_key="idem-invalid-create")
    with pytest.raises(RuntimeValidationError):
        operations.transition_task_state(
            "task-invalid",
            "validated",
            actor_role="SUBCHAT_IMPLEMENTATION",
            idempotency_key="idem-invalid-transition",
        )


@pytest.mark.parametrize("terminal_state", TERMINAL_STATES)
def test_terminal_states_have_no_outgoing_transitions(operations, terminal_state: str) -> None:
    operations.create_task(sample_task(f"task-terminal-{terminal_state}", lifecycle_state=terminal_state), idempotency_key=f"idem-terminal-create-{terminal_state}")
    with pytest.raises(RuntimeValidationError):
        operations.transition_task_state(
            f"task-terminal-{terminal_state}",
            "assigned",
            actor_role="SUBCHAT_IMPLEMENTATION",
            idempotency_key=f"idem-terminal-transition-{terminal_state}",
        )
