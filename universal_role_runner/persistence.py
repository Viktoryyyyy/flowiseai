from __future__ import annotations

import copy

from .models import CONTRACT_VERSION, PROJECT_NAME, JsonDict
from .schema_validation import validate_pm_l3_decision, validate_role_output


def build_role_output(
    *,
    role_output_id: str,
    role_task_id: str,
    producing_role: str,
    output_type: str,
    payload: JsonDict,
    created_at: str,
    validation_status: str = "schema_valid",
    evidence_refs: list[JsonDict] | None = None,
    blockers: list[JsonDict] | None = None,
    project: str = PROJECT_NAME,
    lane: str = "flowiseai_pm_orchestration",
    execution_mode: str = "browser_chatgpt_github_direct",
    metadata: JsonDict | None = None,
) -> JsonDict:
    merged_metadata: JsonDict = {
        "project": project,
        "lane": lane,
        "execution_mode": execution_mode,
        "extensions": {"role_output_id": role_output_id},
    }
    if metadata:
        merged_metadata.update(metadata)
        extensions = dict(metadata.get("extensions", {})) if isinstance(metadata.get("extensions"), dict) else {}
        extensions.setdefault("role_output_id", role_output_id)
        merged_metadata["extensions"] = extensions

    role_output: JsonDict = {
        "contract_version": CONTRACT_VERSION,
        "role_output_id": role_output_id,
        "role_task_id": role_task_id,
        "producing_role": producing_role,
        "structured_payload": {
            "output_type": output_type,
            "payload": payload,
        },
        "validation_status": validation_status,
        "immutable_persistence": {
            "persisted": False,
            "persistence_marker": "append_only_role_output",
            "mutation_policy": "append_new_version_only",
            "replacement_policy": "forbidden",
        },
        "evidence_refs": evidence_refs or [],
        "blockers": blockers or [],
        "created_at": created_at,
        "metadata": merged_metadata,
    }
    return validate_role_output(role_output)


def role_output_to_state_api_payload(
    role_output: JsonDict,
    *,
    project: str | None = None,
    lane: str | None = None,
    execution_mode: str | None = None,
) -> JsonDict:
    """Create a State API-compatible immutable role output payload.

    RoleOutput contracts use role_task_id/producing_role, while the existing
    StateApiOperations.persist_role_output public method requires task_id and
    reads role for audit metadata. This adapter does not change either schema
    or State API runtime internals.
    """

    validated = validate_role_output(role_output)
    payload = copy.deepcopy(validated)
    metadata = payload.setdefault("metadata", {})
    extensions = metadata.setdefault("extensions", {})
    extensions.setdefault("role_output_id", validated["role_output_id"])

    payload["task_id"] = validated["role_task_id"]
    payload["role"] = validated["producing_role"]
    payload["project"] = project or str(metadata.get("project") or PROJECT_NAME)
    payload["lane"] = lane or str(metadata.get("lane") or "")
    payload["execution_mode"] = execution_mode or str(metadata.get("execution_mode") or "")
    return payload


def build_pm_l3_decision_role_output(
    *,
    decision: JsonDict,
    role_task_id: str,
    role_output_id: str,
    created_at: str,
    producing_role: str = "PM_L3_DELIVERY_VALIDATION_OWNER",
    project: str = PROJECT_NAME,
    lane: str = "flowiseai_pm_orchestration",
    execution_mode: str = "browser_chatgpt_github_direct",
    evidence_refs: list[JsonDict] | None = None,
) -> JsonDict:
    validate_pm_l3_decision(decision)
    return build_role_output(
        role_output_id=role_output_id,
        role_task_id=role_task_id,
        producing_role=producing_role,
        output_type="decision_report",
        payload=decision,
        created_at=created_at,
        evidence_refs=evidence_refs,
        project=project,
        lane=lane,
        execution_mode=execution_mode,
    )
