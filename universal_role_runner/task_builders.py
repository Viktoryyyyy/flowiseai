from __future__ import annotations

import copy

from .models import CONTRACT_VERSION, PROJECT_NAME, JsonDict
from .schema_validation import validate_role_task


def build_role_task(
    *,
    role_task_id: str,
    phase_run_id: str,
    lane: str,
    assigned_role: str,
    approved_scope: list[str],
    forbidden_scope: list[str],
    acceptance_criteria: list[str],
    created_at: str,
    execution_mode: str = "browser_chatgpt_github_direct",
    context_delivery_mode: str = "inline_copy_block",
    role_context_ref: str = "SUBCHAT_IMPLEMENTATION",
    dynamic_context: JsonDict | None = None,
    status: str = "created",
    metadata: JsonDict | None = None,
) -> JsonDict:
    payload: JsonDict = {
        "contract_version": CONTRACT_VERSION,
        "role_task_id": role_task_id,
        "phase_run_id": phase_run_id,
        "project": PROJECT_NAME,
        "lane": lane,
        "execution_mode": execution_mode,
        "assigned_role": assigned_role,
        "input_context": {
            "context_delivery_mode": context_delivery_mode,
            "role_context_ref": role_context_ref,
            "dynamic_context": dynamic_context or {},
        },
        "approved_scope": approved_scope,
        "forbidden_scope": forbidden_scope,
        "acceptance_criteria": acceptance_criteria,
        "lease_ref": {"required": True, "lease_id": None},
        "status": status,
        "retry_metadata": {
            "attempt_count": 0,
            "max_attempts": 3,
            "retry_state": "not_retryable",
            "last_failure_code": None,
        },
        "output_ref": {"role_output_id": None, "immutable": True},
        "created_at": created_at,
    }
    if metadata is not None:
        payload["metadata"] = metadata
    return validate_role_task(payload)


def role_task_to_state_api_task(role_task: JsonDict) -> JsonDict:
    """Map RoleTask.role_task_id to the State API task_id expected by runtime.

    The State API runtime is intentionally not changed. This adapter preserves
    the original RoleTask fields and adds State API mirror fields only in the
    payload passed to StateApiOperations.create_task.
    """

    validated = validate_role_task(role_task)
    task = copy.deepcopy(validated)
    task["task_id"] = validated["role_task_id"]
    task.setdefault("lifecycle_state", "created")
    task["approved_file_scope"] = list(validated["approved_scope"])
    task["forbidden_file_scope"] = list(validated["forbidden_scope"])
    task.setdefault("metadata", {}).setdefault("extensions", {})["role_task_id"] = validated["role_task_id"]
    return task
