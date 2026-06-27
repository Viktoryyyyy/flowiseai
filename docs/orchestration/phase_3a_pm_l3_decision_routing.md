# Phase 3A PM L3 Decision Routing Handler

Status: Phase 3A repository-local implementation  
Project: MOEX Bot  
Lane: flowiseai_pm_orchestration  
Execution mode: browser_chatgpt_github_direct

## Purpose

Phase 3A adds deterministic interpretation of validated PM L3 decisions. The routing handler converts a PM L3 decision into a next-step artifact that can be persisted or handed to a later orchestration step.

## Supported decision types

The handler supports the required Phase 3A decision types:

- `route_next_role`
- `accept_role_output`
- `reject_role_output`
- `request_correction`
- `raise_blocker`
- `return_to_pm_l2`
- `complete_phase_step`

## Repository-local boundary

The handler produces data only. It does not execute:

- GitHub mutations;
- server apply;
- deployment;
- deployed runtime smoke;
- Flowise installation;
- model calls;
- private endpoint calls.

Every next-step artifact contains explicit side-effect flags set to false.

## Deterministic artifacts

The handler returns:

- routing status;
- decision id;
- decision type;
- next action;
- target role;
- target queue;
- handoff requirement;
- a complete `next_step_artifact`.

## Semantic checks

The existing schema validator remains the first gate. Phase 3A adds routeability checks, including:

- routed role work must include `next_role`, `next_task`, a role execution queue, and `handoff_required=true`;
- accept/complete decisions must include positive acceptance evidence;
- reject decisions must include rejection reasons;
- blocker decisions must include at least one blocker;
- PM L2 returns must target `pm_l2_return` and require handoff generation.

## Acceptance

Phase 3A is acceptable when runtime tests prove every required decision type produces a deterministic artifact and invalid route semantics are rejected without any external side effects.
