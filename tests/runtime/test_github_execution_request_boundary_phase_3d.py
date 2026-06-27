from __future__ import annotations

import pytest

from universal_role_runner import build_github_execution_request, reject_github_execution_request_execution
from universal_role_runner.models import BoundaryViolationError


BASE_SHA = "87990003b478e33ac538fd8847b0cf1a6ec4cc2b"
CREATED_AT = "2026-06-27T00:00:00Z"


@pytest.mark.parametrize(
    "operation_type",
    [
        "create_branch",
        "commit_approved_scope",
        "open_pull_request",
        "verify_ci",
        "merge_request_boundary",
    ],
)
def test_github_execution_request_boundary_represents_required_request_types(operation_type: str) -> None:
    request = build_github_execution_request(
        request_id=f"github-request-{operation_type}",
        phase_run_id="phase-run-3",
        requested_operation_type=operation_type,
        repository_full_name="Viktoryyyyy/flowiseai",
        base_ref="main",
        base_sha=BASE_SHA,
        branch_name="flowiseai-pm/phase-3b-3e-orchestration-loop",
        approved_file_scope=["universal_role_runner/**", "tests/runtime/**"],
        pr_title="Phase 3 repository-local orchestration loop",
        created_at=CREATED_AT,
    )

    assert request["requested_operation_type"] == operation_type
    assert request["result_evidence"]["conclusion"] == "not_started"
    assert request["safety_boundaries"] == {
        "direct_main_write_allowed": False,
        "server_apply_allowed": False,
        "deployment_allowed": False,
        "runtime_smoke_allowed": False,
        "secrets_allowed": False,
        "private_endpoints_allowed": False,
    }
    assert request["secrets"] == []
    assert request["private_endpoints"] == []


def test_github_execution_request_cannot_execute_inside_local_runner() -> None:
    request = build_github_execution_request(
        request_id="github-request-merge-boundary",
        phase_run_id="phase-run-3",
        requested_operation_type="merge_request_boundary",
        repository_full_name="Viktoryyyyy/flowiseai",
        base_ref="main",
        base_sha=BASE_SHA,
        branch_name="flowiseai-pm/phase-3b-3e-orchestration-loop",
        approved_file_scope=["universal_role_runner/**"],
        pr_title="Phase 3 repository-local orchestration loop",
        created_at=CREATED_AT,
    )

    with pytest.raises(BoundaryViolationError):
        reject_github_execution_request_execution(request, attempted_action="merge_pull_request")
