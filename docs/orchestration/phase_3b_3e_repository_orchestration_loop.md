# Phase 3B-3E Repository-Local PM Orchestration Loop

Status: Phase 3B-3E repository-local implementation  
Project: MOEX Bot  
Lane: flowiseai_pm_orchestration  
Execution mode: browser_chatgpt_github_direct

## Scope

This package completes the remaining Phase 3 repository-local orchestration logic after Phase 3A decision routing.

## Phase 3B: browser handoff / copy-block generator

Implemented capability:

- `PM_L2_TO_PM_L3`
- `PM_L3_TO_SUBCHAT`
- `SUBCHAT_TO_PM_L3`
- `PM_L3_TO_PM_L2`

The generator returns a deterministic `HANDOFF_BLOCK` / `END_HANDOFF_BLOCK` text block plus the structured payload used to create it.

## Phase 3C: evidence package aggregator

Implemented capability:

- PR evidence aggregation;
- CI evidence aggregation;
- changed-file scope summary;
- decision trail;
- blockers;
- next action;
- final PM L2 evidence package;
- explicit server/deployment status fields.

## Phase 3D: GitHubExecutionRequest controlled boundary

The request schema now includes the Phase 3 merge boundary operation:

- `merge_request_boundary`

This is a request/evidence boundary only. It does not execute a merge from inside the local runner. Existing boundary enforcement remains: local execution attempts raise `BoundaryViolationError`.

## Phase 3E: repository-local e2e simulation

The e2e test covers the full local cycle:

1. create task;
2. claim task;
3. role output;
4. validation output;
5. PM L3 decision;
6. next routing;
7. final PM L2 handoff;
8. evidence package aggregation.

## Forbidden scope status

Not performed and not implemented:

- server apply;
- deployment;
- runtime smoke against deployed service;
- Flowise install;
- nginx changes;
- docker compose changes;
- VPN changes;
- n8n server changes;
- secrets or private endpoints.

## Acceptance

This package is acceptable only when GitHub Actions `tests` passes on the latest PR head SHA and the PR changed files remain inside repository-local orchestration scope.
