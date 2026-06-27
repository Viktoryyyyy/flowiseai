# Phase 2D Universal Role Runner Contract

Status: contract package only  
Project: MOEX Bot  
Lane: flowiseai_pm_orchestration  
Execution mode: browser_chatgpt_github_direct and future route_b_n8n_universal_role_runner

## Purpose

Phase 2D defines repository contracts for a Universal Role Runner. It does not implement runtime execution. The package specifies how PM L2, PM L3, and Sub-chat role work is represented as deterministic contracts before later runtime or Flowise integration work is authorized.

## Logical architecture

The Universal Role Runner is modeled as a control loop:

PM L2 phase authorization -> PhaseRun -> PM L3 decision -> RoleTask -> TaskClaimLease -> role prompt assembly -> structured role output -> schema validation -> immutable RoleOutput persistence -> PM L3 next decision -> final PM L2 evidence package.

The contracts separate orchestration state from conversational text. Browser copy blocks remain the handoff transport in browser mode. Future automated mode may resolve task context from durable DB or repository references.

## Core contracts

- PhaseRun records phase identity, lane, execution mode, repository, base SHA, branch and PR references, authority boundary, lifecycle status, timestamps, and blockers.
- RoleTask records one assigned role task, input context, approved scope, forbidden scope, acceptance criteria, lease reference, retry metadata, and output reference.
- TaskClaimLease records exclusive task claim semantics, expiration, renewal, release, and reclaim rules.
- RoleOutput records structured role results as immutable persisted outputs, with validation status, evidence references, and blockers.
- PM L3 Decision records routing, acceptance, rejection, blocker, and completion decisions.
- GitHubExecutionRequest records approved GitHub operation requests and evidence boundaries.

## RoleContext resolution

Role context is resolved before prompt assembly. A role task must identify the target role and the dynamic context needed for that role. Browser mode uses an inline copy block. Automated mode must resolve DB or repository references before calling the model.

## Prompt assembly boundary

Prompt assembly may combine static project canon, role context, and dynamic task context. It must not add authority, scope, secrets, private endpoints, runtime claims, server commands, or files outside the approved scope.

## Structured output validation

Every role response intended for orchestration must be parsed into a structured payload. The payload must be validated against the expected schema before it can drive the next orchestration step.

## Immutable RoleOutput persistence

RoleOutput is append-only evidence. It is not mutable conversational state. Corrections create a new role output version or a follow-up role task; they do not rewrite accepted evidence.

## Audit event semantics

Every material state transition should be represented as an audit event in future runtime phases. Audit events must reference the actor, subject, operation, outcome, and evidence. Audit records are append-only.

## Retry, blocker, and correction semantics

A failed role task can be retried only when the retry metadata allows it and the approved scope remains unchanged. A blocker stops the current step until PM L3 or PM L2 resolves it. A correction is a new task or new output, not a silent overwrite.

## Idempotency strategy

Task creation, claim, output persistence, PM L3 decision creation, and GitHub execution request creation must use deterministic identifiers or idempotency keys in future runtime phases. Replayed operations must return the same stored result or the same stored failure semantics.

## Fail-closed rules

The runner must fail closed when the target role, lane, execution mode, approved scope, authority boundary, or schema binding is missing or invalid. It must also fail closed on direct main writes, server apply, deployment, runtime smoke, secrets, or private endpoints unless a future phase explicitly authorizes a different boundary.

## Explicit non-goals

This phase does not implement runtime workers, Flowise nodes, server deployment, database migrations, private endpoints, secret handling, CI configuration, production orchestration, or MOEX strategy behavior.
