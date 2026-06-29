# Phase 17 GitHub Executor Error Hardening

Status: repository contract/documentation/test package  
Project: MOEX Bot + FlowiseAI  
Lane: `flowiseai_pm_orchestration`  
Task: `flowiseai_phase_17_github_executor_error_hardening`

## Goal

Phase 17 converts the Phase 16 controlled sandbox write-smoke into a fail-closed contract package for a future hardened GitHub executor.

This PR does not make the executor production-ready. It defines the contracts and tests that a later Flowise graph hardening phase must satisfy before any GitHub mutation is allowed.

## Phase 16 production gaps

Phase 16 proved that a Flowise AgentFlow V2 graph using HTTP nodes could perform a controlled sandbox GitHub write sequence: branch, allowlisted file, pull request, and CI evidence.

That smoke result is not sufficient for production because the executor still needs deterministic handling for:

- authentication failure or missing credentials;
- insufficient repository permission;
- repository allowlist mismatch;
- stale, missing, or conflicting branch state;
- existing, missing, or conflicting file state;
- duplicate, missing, closed, or ambiguous pull request state;
- rate limit and secondary rate limit responses;
- transient network errors and retry boundaries;
- CI run ambiguity or missing evidence tied to the latest full PR head SHA;
- duplicate request, replay, resume, and idempotency conflicts;
- scope drift between planned files and actual changed files;
- secret exposure in payloads, artifacts, logs, or repository files;
- authority violations such as merge, direct main write, force push, delete, server apply, deployment, or Flowise graph mutation.

## Central fail-closed rule

No GitHub mutation is allowed until all of the following are true:

```text
GitHubPreflightResult.status == pass
GitHubPreflightResult.blockers == []
GitHubPreflightResult.mutation_allowed == true
PM L2 / HITL approval is explicitly recorded
```

Any missing, ambiguous, contradictory, or stale evidence returns `blocked` or `failed`, never partial approval.

## Contract files

Phase 17 adds three repository contracts:

```text
contracts/github/github_executor_preflight_request.schema.json
contracts/github/github_executor_preflight_result.schema.json
contracts/github/github_execution_result.schema.json
```

### GitHubExecutorPreflightRequest

The request schema captures the planned operation before mutation. It requires repository identity, base branch and SHA, target branch, approved file scope, idempotency key, requester/source role, authority profile, and PM L2/HITL approval reference.

The authority profile is intentionally restrictive:

- no direct main write;
- no merge;
- no force push;
- no delete;
- no server apply;
- no deployment;
- no Flowise graph mutation;
- no secrets.

### GitHubPreflightResult

The result schema records preflight checks and blockers. It contains exact enumerable blocker codes for every Phase 17 GitHub error class. A `pass` result with any blocker is invalid. A `blocked` or `failed` result without blocker evidence is invalid.

### GitHubExecutionResult

The execution result schema records the post-write evidence only after allowed mutation. It binds mutation permission to a pass preflight plus PM L2/HITL approval. It also records branch, commit/head SHA, changed files, pull request state, CI workflow/run/job status, and whether evidence is tied to the latest PR head SHA.

## Error taxonomy and blocker behavior

| Error class | Blocker code | Fail-closed behavior |
| --- | --- | --- |
| auth | `github_auth_missing_or_invalid` | Block before any mutation when credentials are absent, invalid, expired, or rejected. |
| permissions | `github_permission_insufficient` | Block before mutation when token/user lacks required repo permissions. |
| repo allowlist | `github_repo_not_allowlisted` | Block if `repository_full_name` is not explicitly allowlisted. |
| branch state | `github_branch_state_invalid` | Block if base or target branch state is stale, missing, polluted, or conflicts with expected SHA. |
| file state | `github_file_state_conflict` | Block or resume only through explicit idempotency rules when file existence/content conflicts. |
| PR state | `github_pr_state_conflict` | Block or resume when PR is duplicate, missing, closed, or targets unexpected base/head. |
| rate limits | `github_rate_limit_blocked` | Block and return retry evidence; do not guess success. |
| network errors | `github_network_error` | Block or retry only inside the approved idempotency envelope. |
| CI ambiguity | `github_ci_ambiguity` | Block if CI evidence cannot be tied to the latest full PR head SHA. |
| duplicate/retry/idempotency | `github_idempotency_conflict` | Resume only if request, branch, file scope, PR, and head SHA match the idempotency key. |
| scope drift | `github_scope_drift` | Block if actual changed files differ from approved file scope. |
| secret exposure | `github_secret_exposure` | Block immediately and do not commit or echo secret values. |
| authority violation | `github_authority_violation` | Block if any forbidden operation is requested or observed. |

## Idempotency and resume rules

A repeated request may resume only when all of these are true:

1. `idempotency_key` matches the original request.
2. Repository, base branch, target branch, and approved file scope are identical.
3. Existing branch head is compatible with the expected operation.
4. Existing file content is either absent or exactly matches the expected artifact set.
5. Existing PR is open, targets the expected base branch, and uses the expected head branch.
6. CI evidence is checked against the latest full PR head SHA.

If any field differs, the executor must return a blocker instead of writing.

## Production readiness status

Phase 17 is not production executor readiness. It is a repository contract package only.

Flowise graph hardening is deferred to Phase 18. Phase 18 must update the Flowise AgentFlow V2 graph so it emits and consumes these contracts deterministically before any GitHub mutation. No Flowise graph update, runtime smoke, deployment, server apply, or merge is part of Phase 17.

## Validation

The contract test file validates that:

- all three JSON schemas are Draft 2020-12 schemas;
- blocker codes cover all required Phase 17 error classes;
- preflight cannot pass with blockers;
- mutation is blocked unless preflight status is `pass`;
- PM L2/HITL approval is required before mutation;
- post-write evidence fields exist in the execution result contract;
- authority violations are represented as blockers.
