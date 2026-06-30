from __future__ import annotations

import pathlib


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
SPEC_PATH = REPO_ROOT / "docs" / "orchestration" / "phase_18_flowise_graph_fail_closed_hardening_spec.md"

REQUIRED_CHECKS = {
    "repo_allowlist_check",
    "branch_state_check",
    "file_state_check",
    "pr_state_check",
    "auth_check",
    "permission_check",
    "rate_limit_check",
    "network_check",
    "ci_ambiguity_check",
    "idempotency_resume_check",
    "scope_check",
    "authority_check",
    "secret_exposure_check",
}

REQUIRED_BLOCKER_CODES = {
    "github_auth_missing_or_invalid",
    "github_permission_insufficient",
    "github_repo_not_allowlisted",
    "github_branch_state_invalid",
    "github_file_state_conflict",
    "github_pr_state_conflict",
    "github_rate_limit_blocked",
    "github_network_error",
    "github_ci_ambiguity",
    "github_idempotency_conflict",
    "github_scope_drift",
    "github_secret_exposure",
    "github_authority_violation",
}

REQUIRED_NODE_GROUP_TERMS = {
    "GitHubExecutorPreflightRequest builder",
    "read-only GitHub evidence collectors",
    "required preflight check builders",
    "GitHubPreflightResult builder",
    "schema validator for GitHubPreflightResult",
    "Fail-Closed Router",
    "PM L2 / HITL Approval Gate",
    "immutable write plan builder",
    "approved_scope_hash comparison",
    "mutation boundary",
    "post-write evidence verifier",
    "GitHubExecutionResult builder",
    "schema validator for GitHubExecutionResult",
    "sanitized final Direct Reply",
}

FAIL_CLOSED_TERMS = {
    "status == pass",
    "blockers == []",
    "mutation_allowed == true",
    "default route is blocked",
    "PM L2 / HITL approval",
    "approved_scope_hash",
}

MUTATION_BOUNDARY_TERMS = {
    "No GitHub POST/PUT/PATCH/DELETE before preflight pass",
    "Read-only GitHub GET evidence collection",
}

POST_WRITE_EVIDENCE_FIELDS = {
    "branch",
    "commit_sha",
    "head_sha",
    "changed_files",
    "pull_request.number",
    "pull_request.url",
    "pull_request.state",
    "ci.workflow",
    "ci.run_id",
    "ci.job",
    "ci.conclusion",
    "ci.evidence_tied_to_head_sha",
    "authority_boundary",
}

PR_SPLIT_TERMS = {"PR_18C", "PR_18D", "PR_18E"}

NON_GOAL_TERMS = {
    "No runtime import",
    "No server apply",
    "No runtime smoke",
    "No production readiness",
}


def _spec_text() -> str:
    assert SPEC_PATH.exists(), f"Missing Phase 18C spec document: {SPEC_PATH}"
    return SPEC_PATH.read_text(encoding="utf-8")


def _assert_all_present(text: str, required_terms: set[str]) -> None:
    missing = sorted(term for term in required_terms if term not in text)
    assert not missing, f"Missing required Phase 18 spec terms: {missing}"


def test_phase_18_spec_document_exists() -> None:
    assert SPEC_PATH.exists()


def test_phase_18_spec_contains_required_check_names() -> None:
    _assert_all_present(_spec_text(), REQUIRED_CHECKS)


def test_phase_18_spec_contains_required_blocker_codes() -> None:
    _assert_all_present(_spec_text(), REQUIRED_BLOCKER_CODES)


def test_phase_18_spec_contains_required_node_groups() -> None:
    _assert_all_present(_spec_text(), REQUIRED_NODE_GROUP_TERMS)


def test_phase_18_spec_contains_fail_closed_routing_terms() -> None:
    _assert_all_present(_spec_text(), FAIL_CLOSED_TERMS)


def test_phase_18_spec_contains_mutation_boundary_terms() -> None:
    _assert_all_present(_spec_text(), MUTATION_BOUNDARY_TERMS)


def test_phase_18_spec_contains_post_write_evidence_fields() -> None:
    _assert_all_present(_spec_text(), POST_WRITE_EVIDENCE_FIELDS)


def test_phase_18_spec_contains_pr_split_terms() -> None:
    _assert_all_present(_spec_text(), PR_SPLIT_TERMS)


def test_phase_18_spec_contains_non_goal_terms() -> None:
    _assert_all_present(_spec_text(), NON_GOAL_TERMS)
