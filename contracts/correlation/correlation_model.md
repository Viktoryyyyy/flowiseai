# Phase 8 Correlation and Idempotency Model

Status: contract artifact only  
Project: MOEX Bot + FlowiseAI  
Phase: Phase 8  
Lane: flowiseai_pm_orchestration

## Purpose

This document defines how Phase 8 artifacts preserve traceability across:

- `PM_L3_TaskEnvelope`;
- `FlowiseRunRequest`;
- `FlowiseRunResult`.

It does not define runtime storage, network transport, Flowise deployment, production graph behavior, or server execution.

## Required identifiers

| Field | Required in | Rule |
|---|---|---|
| `correlation_id` | PM_L3_TaskEnvelope, FlowiseRunRequest, FlowiseRunResult | Same value across one end-to-end role-task execution. |
| `task_id` | PM_L3_TaskEnvelope, FlowiseRunRequest | Same logical task identifier from PM L3 handoff. |
| `request_id` | FlowiseRunRequest, FlowiseRunResult | Result must echo the originating request id. |
| `idempotency_key` | FlowiseRunRequest, FlowiseRunResult | Result must echo the originating idempotency key. |
| `result_id` | FlowiseRunResult | Unique result envelope id for the returned execution result. |

## Correlation echo rules

1. PM L3 creates one `correlation_id` for a role-task envelope.
2. `FlowiseRunRequest.correlation_id` must equal `PM_L3_TaskEnvelope.correlation_id`.
3. `FlowiseRunResult.correlation_id` must equal `FlowiseRunRequest.correlation_id`.
4. `FlowiseRunResult.request_id` must equal `FlowiseRunRequest.request_id`.
5. `FlowiseRunResult.idempotency_key` must equal `FlowiseRunRequest.idempotency_key`.

## Idempotency rule

For the same `idempotency_key`, the execution surface must not create conflicting semantic results. Replays may return the same result or an explicitly marked no-op, but they must not claim a second divergent execution.

## Authority boundary propagation

The request and result both carry fail-closed authority fields. A valid Phase 8 exchange cannot claim any of these actions as allowed or performed:

- direct write to `main`;
- merge without PM L2 authority;
- server changes;
- deployment;
- Flowise runtime modification;
- production graph change;
- secret exposure.

## Non-goals

This model does not choose a database, queue, Flowise endpoint, authentication method, deployment path, server path, or runtime graph implementation.
