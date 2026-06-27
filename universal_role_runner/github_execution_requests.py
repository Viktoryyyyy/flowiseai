from __future__ import annotations

from .models import CONTRACT_VERSION, BoundaryViolationError, JsonDict
from .schema_validation import validate_github_execution_request


_FORBIDDEN_EXECUTION_MESSAGE = "GitHubExecutionRequest execution is blocked in the Phase 2E local/dev runner."


def build_github_execution_request(
    *,
    request_id: str,
    phase_run_id: str,
    requested_operation_type: str,
    repository_full_name: str,
    base_ref: str,
    base_sha: str,
    branch_name: str,
    approved_file_scope: list[str],
    pr_title: str,
    created_at: str,
    workflow_name: str | None = "tests",
    draft: bool = False,
    base_branch: str | None = None,
    metadata: JsonDict | None = None,
) -> JsonDict:
    request: JsonDict = {
        "contract_version": CONTRACT_VERSION,
        "request_id": request_id,
        "phase_run_id": phase_run_id,
        "requested_operation_type": requested_operation_type,
        "repository_full_name": repository_full_name,
        "base_ref": base_ref,
        "base_sha": base_sha,
        "branch_name": branch_name,
        "approved_file_scope": approved_file_scope,
        "pr_metadata": {
            "title": pr_title,
            "body_required": True,
            "base_branch": base_branch or base_ref,
            "draft": draft,
        },
        "ci_expectation": {
            "ci_required": True,
            "workflow_name": workflow_name,
            "evidence_must_match_head_sha": True,
        },
        "result_evidence": {
            "commit_sha": None,
            "pr_number": None,
            "workflow_run_id": None,
            "conclusion": "not_started",
        },
        "safety_boundaries": {
            "direct_main_write_allowed": False,
            "server_apply_allowed": False,
            "deployment_allowed": False,
            "runtime_smoke_allowed": False,
            "secrets_allowed": False,
            "private_endpoints_allowed": False,
        },
        "secrets": [],
        "private_endpoints": [],
        "created_at": created_at,
    }
    if metadata is not None:
        request["metadata"] = metadata
    return validate_github_execution_request(request)


def reject_github_execution_request_execution(
    request: JsonDict,
    *,
    attempted_action: str = "execute",
) -> None:
    validate_github_execution_request(request)
    raise BoundaryViolationError(
        _FORBIDDEN_EXECUTION_MESSAGE,
        {
            "attempted_action": attempted_action,
            "requested_operation_type": request["requested_operation_type"],
            "safety_boundaries": request["safety_boundaries"],
        },
    )