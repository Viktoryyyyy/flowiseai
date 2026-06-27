from __future__ import annotations

import re
from typing import Any

from .models import (
    EXECUTION_MODES,
    GITHUB_REQUEST_CONCLUSIONS,
    GITHUB_REQUEST_OPERATION_TYPES,
    PM_L3_DECISION_TYPES,
    PROJECT_NAME,
    ROLE_OUTPUT_TYPES,
    ROLE_TASK_STATUSES,
    JsonDict,
    SchemaValidationError,
)

_VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")
_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
_REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


def _obj(value: Any, name: str) -> JsonDict:
    if not isinstance(value, dict):
        raise SchemaValidationError(f"{name} must be an object")
    return value


def _required(payload: JsonDict, fields: set[str], name: str) -> None:
    missing = sorted(fields - set(payload))
    if missing:
        raise SchemaValidationError(f"{name} missing required fields", {"missing": missing})


def _str(payload: JsonDict, field: str, *, nullable: bool = False, min_length: int = 1) -> str | None:
    value = payload.get(field)
    if nullable and value is None:
        return None
    if not isinstance(value, str) or len(value) < min_length:
        raise SchemaValidationError(f"{field} must be a non-empty string")
    return value


def _enum(payload: JsonDict, field: str, allowed: set[str]) -> str:
    value = _str(payload, field)
    assert isinstance(value, str)
    if value not in allowed:
        raise SchemaValidationError(f"{field} has unsupported value", {"value": value})
    return value


def _version(payload: JsonDict) -> None:
    value = _str(payload, "contract_version")
    assert isinstance(value, str)
    if not _VERSION_RE.match(value):
        raise SchemaValidationError("contract_version must use semantic version format")


def _string_array(payload: JsonDict, field: str) -> None:
    value = payload.get(field)
    if not isinstance(value, list) or not value or any(not isinstance(item, str) or not item for item in value):
        raise SchemaValidationError(f"{field} must be a non-empty string array")


def _bool(payload: JsonDict, field: str) -> None:
    if not isinstance(payload.get(field), bool):
        raise SchemaValidationError(f"{field} must be a boolean")


def _int_or_null(payload: JsonDict, field: str, minimum: int) -> None:
    value = payload.get(field)
    if value is not None and (isinstance(value, bool) or not isinstance(value, int) or value < minimum):
        raise SchemaValidationError(f"{field} must be null or an integer >= {minimum}")


def _sha_or_null(payload: JsonDict, field: str) -> None:
    value = payload.get(field)
    if value is not None and (not isinstance(value, str) or not _SHA_RE.match(value)):
        raise SchemaValidationError(f"{field} must be null or a 40-character lowercase SHA")


def _blockers(values: Any) -> None:
    if not isinstance(values, list):
        raise SchemaValidationError("blockers must be an array")
    for item in values:
        blocker = _obj(item, "blocker")
        _required(blocker, {"code", "message", "severity"}, "blocker")
        _str(blocker, "code")
        _str(blocker, "message")
        _enum(blocker, "severity", {"info", "warning", "blocking"})


def validate_role_task(payload: JsonDict) -> JsonDict:
    role_task = _obj(payload, "role_task")
    required = {
        "contract_version", "role_task_id", "phase_run_id", "project", "lane",
        "execution_mode", "assigned_role", "input_context", "approved_scope",
        "forbidden_scope", "acceptance_criteria", "lease_ref", "status",
        "retry_metadata", "output_ref", "created_at",
    }
    _required(role_task, required, "role_task")
    extra = sorted(set(role_task) - (required | {"updated_at", "metadata"}))
    if extra:
        raise SchemaValidationError("role_task has unsupported fields", {"extra": extra})
    _version(role_task)
    _str(role_task, "role_task_id")
    _str(role_task, "phase_run_id")
    if role_task.get("project") != PROJECT_NAME:
        raise SchemaValidationError("project must be MOEX Bot")
    _str(role_task, "lane")
    _enum(role_task, "execution_mode", EXECUTION_MODES)
    _str(role_task, "assigned_role")
    _string_array(role_task, "approved_scope")
    _string_array(role_task, "forbidden_scope")
    _string_array(role_task, "acceptance_criteria")
    _enum(role_task, "status", ROLE_TASK_STATUSES)
    _str(role_task, "created_at", min_length=20)

    context = _obj(role_task["input_context"], "input_context")
    _required(context, {"context_delivery_mode", "role_context_ref", "dynamic_context"}, "input_context")
    _enum(context, "context_delivery_mode", {"inline_copy_block", "n8n_db_ref", "repo_ref"})
    _str(context, "role_context_ref")
    _obj(context["dynamic_context"], "dynamic_context")

    lease = _obj(role_task["lease_ref"], "lease_ref")
    _required(lease, {"required", "lease_id"}, "lease_ref")
    _bool(lease, "required")
    _str(lease, "lease_id", nullable=True)

    retry = _obj(role_task["retry_metadata"], "retry_metadata")
    _required(retry, {"attempt_count", "max_attempts", "retry_state", "last_failure_code"}, "retry_metadata")
    if isinstance(retry["attempt_count"], bool) or not isinstance(retry["attempt_count"], int) or retry["attempt_count"] < 0:
        raise SchemaValidationError("attempt_count must be an integer >= 0")
    _int_or_null(retry, "max_attempts", 0)
    _enum(retry, "retry_state", {"not_retryable", "retry_allowed", "retry_scheduled", "retry_exhausted"})
    _str(retry, "last_failure_code", nullable=True)

    output_ref = _obj(role_task["output_ref"], "output_ref")
    _required(output_ref, {"role_output_id", "immutable"}, "output_ref")
    _str(output_ref, "role_output_id", nullable=True)
    if output_ref.get("immutable") is not True:
        raise SchemaValidationError("output_ref.immutable must be true")
    return role_task


def validate_role_output(payload: JsonDict) -> JsonDict:
    role_output = _obj(payload, "role_output")
    required = {
        "contract_version", "role_output_id", "role_task_id", "producing_role",
        "structured_payload", "validation_status", "immutable_persistence",
        "evidence_refs", "blockers", "created_at",
    }
    _required(role_output, required, "role_output")
    extra = sorted(set(role_output) - (required | {"metadata"}))
    if extra:
        raise SchemaValidationError("role_output has unsupported fields", {"extra": extra})
    _version(role_output)
    _str(role_output, "role_output_id")
    _str(role_output, "role_task_id")
    _str(role_output, "producing_role")
    _enum(role_output, "validation_status", {"not_validated", "schema_valid", "schema_invalid", "accepted", "rejected"})
    _str(role_output, "created_at", min_length=20)

    structured = _obj(role_output["structured_payload"], "structured_payload")
    _required(structured, {"output_type", "payload"}, "structured_payload")
    _enum(structured, "output_type", ROLE_OUTPUT_TYPES)
    _obj(structured["payload"], "structured_payload.payload")

    immutable = _obj(role_output["immutable_persistence"], "immutable_persistence")
    _required(immutable, {"persisted", "persistence_marker", "mutation_policy", "replacement_policy"}, "immutable_persistence")
    _bool(immutable, "persisted")
    if immutable.get("persistence_marker") != "append_only_role_output":
        raise SchemaValidationError("invalid persistence marker")
    if immutable.get("mutation_policy") != "append_new_version_only":
        raise SchemaValidationError("invalid mutation policy")
    if immutable.get("replacement_policy") != "forbidden":
        raise SchemaValidationError("invalid replacement policy")
    if not isinstance(role_output["evidence_refs"], list):
        raise SchemaValidationError("evidence_refs must be an array")
    _blockers(role_output["blockers"])
    return role_output


def validate_pm_l3_decision(payload: JsonDict) -> JsonDict:
    decision = _obj(payload, "pm_l3_decision")
    required = {
        "contract_version", "decision_id", "phase_run_id", "decision_type",
        "next_role", "next_task", "routing_target", "acceptance_details",
        "rejection_details", "blocker_details", "created_at",
    }
    _required(decision, required, "pm_l3_decision")
    _version(decision)
    _str(decision, "decision_id")
    _str(decision, "phase_run_id")
    _enum(decision, "decision_type", PM_L3_DECISION_TYPES)
    _str(decision, "next_role", nullable=True)
    if decision["next_task"] is not None:
        _obj(decision["next_task"], "next_task")
    _str(decision, "created_at", min_length=20)

    routing = _obj(decision["routing_target"], "routing_target")
    _required(routing, {"target_role", "target_queue", "handoff_required"}, "routing_target")
    _str(routing, "target_role", nullable=True)
    _enum(routing, "target_queue", {"browser_chat", "n8n_role_task_queue", "pm_l2_return", "none"})
    _bool(routing, "handoff_required")

    acceptance = _obj(decision["acceptance_details"], "acceptance_details")
    _required(acceptance, {"accepted", "criteria_met"}, "acceptance_details")
    _bool(acceptance, "accepted")
    if not isinstance(acceptance["criteria_met"], list) or any(not isinstance(item, str) for item in acceptance["criteria_met"]):
        raise SchemaValidationError("criteria_met must be an array of strings")

    rejection = _obj(decision["rejection_details"], "rejection_details")
    _required(rejection, {"rejected", "reasons"}, "rejection_details")
    _bool(rejection, "rejected")
    if not isinstance(rejection["reasons"], list) or any(not isinstance(item, str) for item in rejection["reasons"]):
        raise SchemaValidationError("reasons must be an array of strings")

    blocker_details = _obj(decision["blocker_details"], "blocker_details")
    _required(blocker_details, {"blocked", "blockers"}, "blocker_details")
    _bool(blocker_details, "blocked")
    _blockers(blocker_details["blockers"])
    return decision


def validate_github_execution_request(payload: JsonDict) -> JsonDict:
    request = _obj(payload, "github_execution_request")
    required = {
        "contract_version", "request_id", "phase_run_id", "requested_operation_type",
        "repository_full_name", "base_ref", "base_sha", "branch_name",
        "approved_file_scope", "pr_metadata", "ci_expectation", "result_evidence",
        "safety_boundaries", "secrets", "private_endpoints", "created_at",
    }
    _required(request, required, "github_execution_request")
    _version(request)
    _str(request, "request_id")
    _str(request, "phase_run_id")
    _enum(request, "requested_operation_type", GITHUB_REQUEST_OPERATION_TYPES)
    repo = _str(request, "repository_full_name")
    assert isinstance(repo, str)
    if not _REPO_RE.match(repo):
        raise SchemaValidationError("repository_full_name must be owner/name")
    base_sha = _str(request, "base_sha")
    assert isinstance(base_sha, str)
    if not _SHA_RE.match(base_sha):
        raise SchemaValidationError("base_sha must be a 40-character lowercase SHA")
    _str(request, "base_ref")
    _str(request, "branch_name")
    _string_array(request, "approved_file_scope")
    _str(request, "created_at", min_length=20)

    pr = _obj(request["pr_metadata"], "pr_metadata")
    _required(pr, {"title", "body_required", "base_branch", "draft"}, "pr_metadata")
    _str(pr, "title")
    _bool(pr, "body_required")
    _str(pr, "base_branch")
    _bool(pr, "draft")

    ci = _obj(request["ci_expectation"], "ci_expectation")
    _required(ci, {"ci_required", "workflow_name", "evidence_must_match_head_sha"}, "ci_expectation")
    _bool(ci, "ci_required")
    _str(ci, "workflow_name", nullable=True)
    if ci.get("evidence_must_match_head_sha") is not True:
        raise SchemaValidationError("evidence must match head SHA")

    result = _obj(request["result_evidence"], "result_evidence")
    _required(result, {"commit_sha", "pr_number", "workflow_run_id", "conclusion"}, "result_evidence")
    _sha_or_null(result, "commit_sha")
    _int_or_null(result, "pr_number", 1)
    _int_or_null(result, "workflow_run_id", 1)
    _enum(result, "conclusion", GITHUB_REQUEST_CONCLUSIONS)

    safety = _obj(request["safety_boundaries"], "safety_boundaries")
    for key in {
        "direct_main_write_allowed",
        "server_apply_allowed",
        "deployment_allowed",
        "runtime_smoke_allowed",
        "secrets_allowed",
        "private_endpoints_allowed",
    }:
        if safety.get(key) is not False:
            raise SchemaValidationError(f"safety_boundaries.{key} must be false")
    if request["secrets"] != []:
        raise SchemaValidationError("secrets must be empty")
    if request["private_endpoints"] != []:
        raise SchemaValidationError("private_endpoints must be empty")
    return request
