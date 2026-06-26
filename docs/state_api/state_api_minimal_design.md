# State API Minimal Contract Design

Status: contract/design package only  
Project: MOEX Bot  
Lane: flowiseai_pm_orchestration  
Runtime claim: false  
Implementation status: none

This package formalizes the minimal State API contract for FlowiseAI PM orchestration. It does not implement a service, does not deploy Flowise, does not choose a database engine, does not choose a framework, does not define service topology, does not define auth, and does not define a deployment mechanism.

## Minimal resources

| Resource | Contract role |
| --- | --- |
| Task | Unit of assigned PM work with lane, branch, scope, authority, lifecycle state, and retry/failure metadata. |
| Handoff | Self-contained role context transfer between PM and Sub-chat roles. |
| RoleOutput | Immutable role result persisted as append-new-version-only evidence. |
| AuditEvent | Append-only record of operations, lifecycle movement, lease events, idempotency events, retry/failure events, PR/CI evidence, and blockers. |
| TaskClaimLease | Exclusive finite claim over one task by one worker or role actor. |
| StateSnapshot | Read-only summary of task, handoff, role output, audit, and lease state. |

## Required operations

| Operation | Side effect class |
| --- | --- |
| create_task | Mutating contract operation. |
| read_task | Read-only contract operation. |
| transition_task_state | Mutating contract operation. |
| claim_next_task | Mutating contract operation. |
| renew_task_lease | Mutating contract operation. |
| release_task_lease | Mutating contract operation. |
| persist_handoff | Mutating contract operation. |
| persist_role_output | Mutating contract operation. |
| append_audit_event | Mutating contract operation. |
| read_state_snapshot | Read-only contract operation. |

All mutating operations are expected to support idempotency at contract level through an idempotency key and deterministic request identity. This package defines the record shape only; it does not choose storage.

## Lifecycle transition table

| From state | Allowed target states |
| --- | --- |
| created | assigned, blocked, failed |
| assigned | running, blocked, failed |
| running | assigned, blocked, completed, validation_pending, failed |
| blocked | assigned, failed |
| completed | validation_pending, validated |
| validation_pending | validated, blocked, failed |
| validated | none |
| failed | none |

`validated` and `failed` are terminal states. No transition out of either terminal state is allowed by the contract.

## Append-only audit model

Audit events are append-only. Existing audit events are not edited or deleted by this contract. Audit events record lifecycle transitions, idempotency outcomes, lease claims, lease renewals, lease releases, retry scheduling, retry attempts, retry exhaustion, failure outcomes, PR/CI evidence, and blocker reports.

The audit model is an evidence model only. It does not define an event bus, database table, queue, index, or retention mechanism.

## Idempotency model

Mutating operations require idempotency at contract level. The request identity is represented by:

- operation name;
- idempotency key;
- request hash;
- task reference where applicable;
- outcome reference.

Replaying the same idempotent request must return or point to the original outcome instead of creating duplicate task, handoff, role output, audit, or lease state. The storage method is intentionally unspecified.

## Exclusive finite claim/lease model

`TaskClaimLease` represents an exclusive finite claim over a task. A task may have at most one active exclusive lease at a time. The contract requires fields for claim time and expiry time, but it does not set TTL defaults or maximum lease duration defaults.

Lease operations are:

- `claim_next_task`;
- `renew_task_lease`;
- `release_task_lease`.

Lease expiry handling is a runtime behavior for a later implementation phase and is not claimed by this package.

## Immutable role output persistence

`RoleOutput` is immutable once persisted. Corrections or replacements must be persisted as a new role output or new version reference. The contract does not define storage, indexing, or retention.

## Read-only StateSnapshot model

`StateSnapshot` is a read-only contract model. It summarizes task states, handoff references, role output references, audit event references, and active lease references. It must not mutate source state and must not be treated as a runtime cache implementation.

## Retry and failure model

Retry is represented through Task metadata plus AuditEvent only. There is no separate retry record schema in this package.

Task retry/failure metadata may include attempt count, retry state, failure state, last failure event reference, last failure reason, next retry time, and backoff policy reference. Audit events record retry scheduling, retry attempts, retry exhaustion, and task failure outcomes.

This package does not choose `max_attempts`, backoff defaults, retry scheduler behavior, worker split, or lease TTL values.

## Runtime boundary

This package is repository contract/design work only.

- `runtime_claim=false`
- no runtime State API service
- no app server code
- no DB migrations
- no DB engine decision
- no Docker, systemd, nginx, TLS, domain, credentials, private endpoints, or raw connection strings
- no Flowise deployment
- no server apply
- no runtime smoke
