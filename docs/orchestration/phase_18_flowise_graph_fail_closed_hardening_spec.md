# Phase 18 Flowise AgentFlow V2 fail-closed hardening spec

Status: Phase 18C spec/test artifact only  
Project: MOEX Bot + FlowiseAI  
Lane: flowiseai_pm_orchestration  
Execution mode: browser_chatgpt_github_direct

## 1. Scope and non-goals

PR_18C is spec/test only. It defines the schema-first Flowise AgentFlow V2 graph hardening target as repository documentation and static contract tests.

Non-goals for PR_18C:

- No graph mutation.
- No graph JSON export.
- No runtime import.
- No server apply.
- No runtime smoke.
- No production readiness.
- No Flowise runtime graph mutation.
- No deployment.
- No merge authority is implied by this document.

This document is an implementation contract for later graph work, not evidence that the live Flowise graph is hardened.

## 2. Source contracts

The Phase 18 graph hardening design is governed by these Phase 17 repository contracts:

- `contracts/github/github_executor_preflight_request.schema.json`
- `contracts/github/github_executor_preflight_result.schema.json`
- `contracts/github/github_execution_result.schema.json`

The Flowise graph must build and validate data that conforms to those contracts before any GitHub write operation is reachable.

## 3. Existing v11 graph risk summary

The existing uploaded v11 graph is treated as a Phase 16 resume/open-PR graph, not as a Phase 17 fail-closed graph.

Known risk summary:

- It is a linear Phase 16 resume/open-PR graph.
- A GitHub POST pull request mutation boundary exists.
- The mutation boundary currently lacks Phase 17 schema-valid preflight pass gate.
- The live runtime graph has not been verified.
- Runtime graph currentness remains unknown.
- Therefore, production readiness is not claimed.

## 4. Required Phase 18 node groups

A hardened AgentFlow V2 graph candidate must include these node groups or directly equivalent node concepts.

| Required node group / concept | Required purpose |
| --- | --- |
| GitHubExecutorPreflightRequest builder | Build a schema-shaped request before GitHub evidence collection and mutation planning. |
| read-only GitHub evidence collectors | Collect repository, branch, file, pull request, auth, permissions, rate-limit, network, CI, idempotency, scope, authority, and secret-safety evidence using read-only operations. |
| required preflight check builders | Convert evidence into the 13 required check objects. |
| GitHubPreflightResult builder | Build a complete preflight result object including status, blockers, mutation_allowed, checks, HITL state, and evidence. |
| schema validator for GitHubPreflightResult | Validate the preflight result against `github_executor_preflight_result.schema.json`. |
| Fail-Closed Router | Route to mutation only when all pass conditions are true; route everything else to blocked. |
| PM L2 / HITL Approval Gate | Require explicit PM L2/HITL approval before write execution. |
| immutable write plan builder | Create the write plan after preflight pass and approval. |
| approved_scope_hash comparison | Compare immutable write plan hash to `approved_scope_hash`. |
| mutation boundary | Contain the first possible GitHub write operation. |
| post-write evidence verifier | Verify branch, commit, head, changed files, PR, CI, and authority evidence after write. |
| GitHubExecutionResult builder | Build the final execution result object. |
| schema validator for GitHubExecutionResult | Validate the final execution result against `github_execution_result.schema.json`. |
| sanitized final Direct Reply | Return only sanitized evidence and no secrets. |

## 5. Required 13 preflight checks mapped to concrete graph nodes

Each check must be represented by a concrete graph node or a clearly named equivalent node. A pass route may not be reached when any check is missing, stale, ambiguous, unexpected, blocked, or failed.

| Check name | Concrete graph node / concept | Minimum evidence expectation |
| --- | --- | --- |
| repo_allowlist_check | Repo Allowlist Check node | Repository equals the approved allowlist target. |
| branch_state_check | Branch State Check node | Target branch state is safe for the planned operation. |
| file_state_check | File State Check node | Target files match the approved create/update expectation and have no conflict. |
| pr_state_check | PR State Check node | Existing PR state is compatible with idempotent resume or new PR creation. |
| auth_check | GitHub Auth Check node | Authentication is present and valid. |
| permission_check | GitHub Permission Check node | Token/user has required repository permission for the planned operation. |
| rate_limit_check | GitHub Rate Limit Check node | Rate-limit state is not blocking. |
| network_check | GitHub Network Check node | GitHub API requests are not failing due to network conditions. |
| ci_ambiguity_check | CI Ambiguity Check node | CI evidence can be tied to the exact PR head SHA. |
| idempotency_resume_check | Idempotency Resume Check node | Retry/resume state is deterministic and does not duplicate writes. |
| scope_check | Approved Scope Check node | Planned changed files exactly match the approved scope. |
| authority_check | Authority Boundary Check node | Merge, direct main write, force push, deletion, server apply, runtime action, and deployment remain outside authority unless explicitly approved. |
| secret_exposure_check | Secret Exposure Check node | Planned output and artifacts contain no secrets or credentials. |

## 6. Required blocker code mapping

Every blocked or failed preflight must map to one or more of these blocker codes. These codes must remain compatible with the Phase 17 schemas.

| Blocker code | Typical source check |
| --- | --- |
| github_auth_missing_or_invalid | auth_check |
| github_permission_insufficient | permission_check |
| github_repo_not_allowlisted | repo_allowlist_check |
| github_branch_state_invalid | branch_state_check |
| github_file_state_conflict | file_state_check |
| github_pr_state_conflict | pr_state_check |
| github_rate_limit_blocked | rate_limit_check |
| github_network_error | network_check |
| github_ci_ambiguity | ci_ambiguity_check |
| github_idempotency_conflict | idempotency_resume_check |
| github_scope_drift | scope_check |
| github_secret_exposure | secret_exposure_check |
| github_authority_violation | authority_check |

## 7. Fail-closed routing contract

The graph routing contract is fail-closed.

Required routing terms:

- The default route is blocked.
- The mutation route is reachable only when `GitHubPreflightResult.status == pass`.
- `status == pass` is required.
- `blockers == []` is required.
- `mutation_allowed == true` is required.
- All 13 required checks have `status == pass`.
- PM L2 / HITL approval is approved.
- PM L2/HITL approval is approved.
- The immutable write plan hash equals `approved_scope_hash`.
- Any missing value routes to blocked output.
- Any ambiguous value routes to blocked output.
- Any stale value routes to blocked output.
- Any unexpected value routes to blocked output.

The blocked route must return a sanitized final Direct Reply and a schema-shaped result/evidence object without executing any mutation.

## 8. Mutation boundary placement

Mutation boundary placement must be explicit and auditable.

Required boundary rules:

- No GitHub POST/PUT/PATCH/DELETE before preflight pass.
- No GitHub POST/PUT/PATCH/DELETE before schema-valid preflight pass.
- Read-only GitHub GET evidence collection is allowed before router.
- The write boundary follows the Fail-Closed Router pass branch plus HITL approval plus immutable plan guard.
- The first GitHub POST, PUT, PATCH, or DELETE operation may occur only after:
  - schema-valid GitHubPreflightResult;
  - `status == pass`;
  - `blockers == []`;
  - `mutation_allowed == true`;
  - all 13 required checks have `status == pass`;
  - PM L2 / HITL approval is approved;
  - immutable write plan hash equals `approved_scope_hash`.

## 9. Post-write evidence contract

After the mutation boundary, the graph must build `GitHubExecutionResult` evidence and validate it against `contracts/github/github_execution_result.schema.json`.

The post-write evidence must map these exact fields:

- `branch`
- `commit_sha`
- `head_sha`
- `changed_files`
- `pull_request.number`
- `pull_request.url`
- `pull_request.state`
- `ci.workflow`
- `ci.run_id`
- `ci.job`
- `ci.conclusion`
- `ci.evidence_tied_to_head_sha`
- `authority_boundary`

The evidence verifier must reject successful execution status if CI evidence cannot be tied to the latest PR head SHA when CI is required.

## 10. Implementation split

Phase 18 is split into separate repository/runtime steps:

- PR_18C: spec/test only.
- PR_18D: sanitized hardened graph JSON export candidate, later and separate.
- PR_18E: controlled runtime import/smoke only after separate PM L2 approval.

PR_18C does not create a sanitized hardened graph JSON export candidate. That artifact is deferred to PR_18D. PR_18C does not perform controlled runtime import/smoke. That action is deferred to PR_18E.
