from __future__ import annotations

import json

from .models import JsonDict, SchemaValidationError


HANDOFF_DIRECTIONS = {
    "PM_L2_TO_PM_L3": ("PM_L2_PHASE_OWNER", "PM_L3_DELIVERY_VALIDATION_OWNER"),
    "PM_L3_TO_SUBCHAT": ("PM_L3_DELIVERY_VALIDATION_OWNER", "SUBCHAT_IMPLEMENTATION"),
    "SUBCHAT_TO_PM_L3": ("SUBCHAT_IMPLEMENTATION", "PM_L3_DELIVERY_VALIDATION_OWNER"),
    "PM_L3_TO_PM_L2": ("PM_L3_DELIVERY_VALIDATION_OWNER", "PM_L2_PHASE_OWNER"),
}

DEFAULT_AUTHORITY_BOUNDARY = {
    "merge_authority": "PM_L3_DELEGATED_FOR_PHASE_3_WITH_CI_AND_SCOPE_PROOF",
    "direct_main_write_allowed": False,
    "server_apply_authority": "not_authorized_in_phase_3",
    "runtime_allowed": "repo_local_tests_only",
}


def _string(value: object, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise SchemaValidationError(f"{field} must be a non-empty string")
    return value


def _list(value: list[object] | None) -> list[object]:
    return list(value or [])


def _roles_for_direction(direction: str, from_role: str | None, to_role: str | None) -> tuple[str, str]:
    if direction not in HANDOFF_DIRECTIONS:
        raise SchemaValidationError("unsupported browser handoff direction", {"direction": direction})
    default_from, default_to = HANDOFF_DIRECTIONS[direction]
    return from_role or default_from, to_role or default_to


def build_browser_handoff_block(
    *,
    direction: str,
    handoff_id: str,
    root_task: str,
    task_id: str,
    current_goal: str,
    exact_task_for_receiver: str,
    created_at: str,
    from_role: str | None = None,
    to_role: str | None = None,
    lane: str = "flowiseai_pm_orchestration",
    execution_mode: str = "browser_chatgpt_github_direct",
    state_as_of: str = "not_checked",
    verified_current_state: list[object] | None = None,
    relevant_repository_state: JsonDict | None = None,
    analysis_summary: str = "none",
    relevant_payload: JsonDict | None = None,
    decisions_already_made: list[object] | None = None,
    approved_scope: list[object] | None = None,
    forbidden_scope: list[object] | None = None,
    blockers: list[object] | None = None,
    unknowns: list[object] | None = None,
    acceptance_criteria: list[object] | None = None,
    required_return_format: JsonDict | None = None,
    authority_boundary: JsonDict | None = None,
    previous_role_report_summary: JsonDict | None = None,
) -> JsonDict:
    """Generate a deterministic browser copy block for the PM orchestration loop."""

    sender, receiver = _roles_for_direction(direction, from_role, to_role)
    payload: JsonDict = {
        "handoff_id": _string(handoff_id, "handoff_id"),
        "handoff_version": 1,
        "project": "MOEX Bot",
        "from_role": sender,
        "to_role": receiver,
        "created_at": _string(created_at, "created_at"),
        "root_task": _string(root_task, "root_task"),
        "task_id": _string(task_id, "task_id"),
        "lane": _string(lane, "lane"),
        "execution_mode": _string(execution_mode, "execution_mode"),
        "current_goal": _string(current_goal, "current_goal"),
        "state_as_of": _string(state_as_of, "state_as_of"),
        "verified_current_state": _list(verified_current_state),
        "relevant_repository_state": relevant_repository_state or {},
        "analysis_summary": analysis_summary,
        "relevant_excerpts_or_structured_payload": relevant_payload or {},
        "decisions_already_made": _list(decisions_already_made),
        "approved_scope": _list(approved_scope),
        "forbidden_scope": _list(forbidden_scope),
        "shared_file_lock": {"required": False, "details": "none"},
        "blockers": _list(blockers),
        "unknowns": _list(unknowns),
        "acceptance_criteria": _list(acceptance_criteria),
        "exact_task_for_receiver": _string(exact_task_for_receiver, "exact_task_for_receiver"),
        "required_first_checks": [
            "confirm target role",
            "confirm lane and execution mode",
            "confirm handoff is self-contained",
            "verify only repository facts that may have changed",
        ],
        "stop_conditions": ["scope widening required", "authority boundary conflict", "state stale"],
        "required_return_format": required_return_format or {"role_step_report": {}},
        "authority_boundary": authority_boundary or DEFAULT_AUTHORITY_BOUNDARY,
        "previous_role_report_summary": previous_role_report_summary or {"done": [], "not_done": [], "blockers": []},
        "expiry_conditions": [
            "relevant origin/main state changed",
            "approved scope changed",
            "newer verified evidence contradicts this handoff",
        ],
    }
    copy_block = "HANDOFF_BLOCK\n" + json.dumps(payload, indent=2, sort_keys=True) + "\nEND_HANDOFF_BLOCK"
    return {"direction": direction, "handoff": payload, "copy_block": copy_block}
