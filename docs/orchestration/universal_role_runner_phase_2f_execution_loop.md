# Universal Role Runner Phase 2F Execution Loop

Status: Phase 2F local/dev execution loop hardening  
Project: MOEX Bot  
Lane: flowiseai_pm_orchestration  
Execution mode: browser_chatgpt_github_direct

## Purpose

Phase 2F adds a narrow one-claim execution loop around the Phase 2E `UniversalRoleRunner` facade.

The loop is repository-local and local/dev only. It converts the existing runtime primitives into a deterministic single-task cycle:

1. claim at most one task for a lane;
2. return `idle` when no lease is available;
3. transition a claimed task to `assigned`;
4. transition the task to `running`;
5. read the task payload;
6. call a supplied local handler;
7. persist one RoleOutput through the existing State API runtime;
8. transition the task to `completed` after output persistence;
9. transition the task to `failed` when handler execution or output persistence raises.

## Boundary

Allowed:

- State API public operations through `UniversalRoleRunner`;
- one local handler callback;
- deterministic idempotency-key derivation from a caller-provided prefix;
- structured loop result payloads for idle, completed, and failed outcomes;
- runtime tests for idle, success, and error-boundary behavior.

Forbidden:

- Flowise server installation;
- external worker service;
- model/API calls from the loop;
- direct GitHub mutation execution;
- server apply;
- deployment;
- deployed runtime smoke;
- secrets or private endpoints.

## Non-goals

This phase does not implement a daemon, queue scheduler, retry backoff engine, Flowise node graph, browser handoff generation, or production service deployment.

## Acceptance

The Phase 2F implementation is acceptable when GitHub Actions `tests` passes on the latest PR head SHA and the PR changed files remain limited to:

- `universal_role_runner/execution_loop.py`;
- execution-loop runtime tests;
- this documentation file.
