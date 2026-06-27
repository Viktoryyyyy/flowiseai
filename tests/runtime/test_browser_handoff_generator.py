from __future__ import annotations

import json

import pytest

from universal_role_runner.browser_handoffs import HANDOFF_DIRECTIONS, build_browser_handoff_block
from universal_role_runner.models import SchemaValidationError


CREATED_AT = "2026-06-27T00:00:00Z"


@pytest.mark.parametrize("direction", sorted(HANDOFF_DIRECTIONS))
def test_browser_handoff_generator_supports_required_directions(direction: str) -> None:
    result = build_browser_handoff_block(
        direction=direction,
        handoff_id=f"handoff-{direction.lower()}",
        root_task="Create FlowiseAI PM Orchestration system",
        task_id="phase-3-browser-handoff",
        current_goal="Generate copy-ready handoff",
        exact_task_for_receiver="Continue the deterministic repository-local cycle",
        created_at=CREATED_AT,
        verified_current_state=[{"fact": "repo-local only", "proof": "test fixture"}],
        approved_scope=["universal_role_runner/**"],
        forbidden_scope=["server filesystem", "deployment"],
        acceptance_criteria=["copy block is self-contained"],
    )

    assert result["direction"] == direction
    assert result["copy_block"].startswith("HANDOFF_BLOCK\n")
    assert result["copy_block"].endswith("\nEND_HANDOFF_BLOCK")
    assert result["handoff"]["from_role"] == HANDOFF_DIRECTIONS[direction][0]
    assert result["handoff"]["to_role"] == HANDOFF_DIRECTIONS[direction][1]
    assert result["handoff"]["authority_boundary"]["server_apply_authority"] == "not_authorized_in_phase_3"

    json_payload = result["copy_block"].removeprefix("HANDOFF_BLOCK\n").removesuffix("\nEND_HANDOFF_BLOCK")
    parsed = json.loads(json_payload)
    assert parsed["handoff_id"] == result["handoff"]["handoff_id"]
    assert parsed["project"] == "MOEX Bot"


def test_browser_handoff_generator_rejects_unknown_direction() -> None:
    with pytest.raises(SchemaValidationError):
        build_browser_handoff_block(
            direction="PM_L1_TO_SERVER",
            handoff_id="bad-handoff",
            root_task="Create FlowiseAI PM Orchestration system",
            task_id="bad-task",
            current_goal="Invalid direction",
            exact_task_for_receiver="Should fail",
            created_at=CREATED_AT,
        )
