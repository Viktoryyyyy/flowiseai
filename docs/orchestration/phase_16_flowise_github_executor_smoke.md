# Phase 16 Flowise GitHub Executor Smoke

status: flowise_originated_write_smoke_artifact
artifact_type: neutral_pre_pr_evidence
correlation_id: corr-flowiseai-phase-16-github-write-executor-20260629
request_id: flowise-run-request-phase-16-github-write-executor-smoke-20260629
task_id: flowiseai_phase_16_flowise_github_executor

## Execution intent

- Flowise graph reached the controlled GitHub write path.
- Branch creation was requested before this file write.
- This file creation was requested inside the allowlisted path only.
- Pull request creation is expected after this file write, but this file does not claim that PR creation has succeeded.

## Scope

repository_full_name: Viktoryyyyy/flowiseai
base_branch: main
branch_name: flowiseai-pm/phase-16-flowise-github-executor-smoke
approved_file_scope: docs/orchestration/phase_16_flowise_github_executor_smoke.md

## Authority boundary

merge_allowed: false
direct_main_write_allowed: false
force_push_allowed: false
delete_branch_allowed: false
delete_file_allowed: false
server_apply_allowed: false
deployment_allowed: false
secrets_allowed: false

## Evidence integrity note

Final PR URL, PR number, changed files, and CI status must be taken only from the final Flowise GitHubExecutionResult sanitizer after GitHub HTTP responses are verified.
