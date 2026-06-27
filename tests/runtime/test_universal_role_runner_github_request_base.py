from __future__ import annotations

from universal_role_runner import build_github_execution_request


CREATED_AT = "2026-06-27T00:00:00Z"
BASE_SHA = "f6b88fd7b617d400173b417e55916d93f53a3baf"


def test_github_execution_request_uses_base_ref_as_default_pr_base_branch() -> None:
    request = build_github_execution_request(
        request_id="github-request-release-base",
        phase_run_id="phase-run-2e",
        requested_operation_type="commit_approved_scope",
        repository_full_name="Viktoryyyyy/flowiseai",
        base_ref="release/phase-2e",
        base_sha=BASE_SHA,
        branch_name="flowiseai-pm/phase-2e-p2-fixes",
        approved_file_scope=["universal_role_runner/**"],
        pr_title="[flowiseai_pm_orchestration] Phase 2E P2 fixes",
        created_at=CREATED_AT,
    )

    assert request["base_ref"] == "release/phase-2e"
    assert request["pr_metadata"]["base_branch"] == "release/phase-2e"


def test_github_execution_request_allows_explicit_pr_base_branch() -> None:
    request = build_github_execution_request(
        request_id="github-request-explicit-base",
        phase_run_id="phase-run-2e",
        requested_operation_type="commit_approved_scope",
        repository_full_name="Viktoryyyyy/flowiseai",
        base_ref="refs/heads/release/phase-2e",
        base_sha=BASE_SHA,
        branch_name="flowiseai-pm/phase-2e-p2-fixes",
        approved_file_scope=["universal_role_runner/**"],
        pr_title="[flowiseai_pm_orchestration] Phase 2E P2 fixes",
        created_at=CREATED_AT,
        base_branch="release/phase-2e",
    )

    assert request["base_ref"] == "refs/heads/release/phase-2e"
    assert request["pr_metadata"]["base_branch"] == "release/phase-2e"
