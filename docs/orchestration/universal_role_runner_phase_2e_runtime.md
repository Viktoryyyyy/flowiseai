# Universal Role Runner Phase 2E Local/Dev Runtime

Status: Phase 2E local/dev runtime skeleton  
Project: MOEX Bot  
Lane: flowiseai_pm_orchestration  
Execution mode: browser_chatgpt_github_direct

## Purpose

This package introduces the first narrow Universal Role Runner runtime facade for local/dev use.

The runtime boundary is intentionally small:

- accept or build RoleTask-shaped payloads;
- map RoleTask.role_task_id to the existing State API task_id required by the runtime;
- create and read tasks through `StateApiOperations`;
- claim work through `StateApiOperations.claim_next_task`;
- transition lifecycle state through `StateApiOperations.transition_task_state`;
- persist RoleOutput through `StateApiOperations.persist_role_output`;
- persist PM L3 Decision as a RoleOutput with `structured_payload.output_type=decision_report`;
- build and validate GitHubExecutionRequest payloads as request artifacts only;
- fail closed for direct GitHub mutation execution, server apply, deployment, runtime smoke, secrets, or private endpoints.

## Public State API dependency

`universal_role_runner` consumes the existing public `StateApiOperations` methods.

It does not change:

- `state_api/runtime/**`;
- `contracts/schemas/**`;
- generated bindings;
- CI configuration;
- dependency files.

The adapter layer exists because the Phase 2D RoleTask and RoleOutput contracts use role-oriented field names, while the Phase 2B State API runtime persists generic task and role-output records.

## Schema validation boundary

Phase 2E does not add dependencies.

`universal_role_runner.schema_validation` is therefore a safe local/dev validator for the fields and enum boundaries used by this phase. It checks required fields, root additional-property restrictions for RoleTask and RoleOutput, relevant nested required fields, enum values, immutable persistence markers, safety boundaries, empty secrets, and private endpoint arrays.

It is not a full JSON Schema draft 2020-12 engine.

## GitHubExecutionRequest semantics

A GitHubExecutionRequest is treated as a request artifact only.

Allowed:

- build request payload;
- validate request payload;
- persist request payload as evidence-style RoleOutput.

Forbidden:

- execute GitHub mutation from the runner;
- write directly to main;
- perform server apply;
- deploy Flowise;
- run deployed runtime smoke;
- carry secrets;
- carry private endpoints.

Any execution attempt raises a fail-closed boundary error.

## Runtime non-goals

This phase does not implement:

- external worker service;
- Flowise node graph;
- Flowise import package;
- Flowise server installation;
- production DB/auth/secrets/monitoring/backup;
- deployed runtime smoke;
- server apply.

## Test coverage

The Phase 2E runtime tests cover:

- create/read/claim/transition/persist RoleOutput lifecycle through public StateApiOperations;
- claim/lease interaction;
- local/dev schema validation for RoleTask, RoleOutput, PM L3 Decision, and GitHubExecutionRequest;
- invalid payload rejection;
- idempotent replay for task creation, RoleOutput persistence, and PM L3 decision persistence;
- PM L3 Decision persistence as RoleOutput `decision_report`;
- GitHubExecutionRequest fail-closed execution boundary.
