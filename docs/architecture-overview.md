# Architecture Overview

## Role model

### PM L1

PM L1 owns the user-facing objective, route selection, and final acceptance context. PM L1 does not implement repository changes.

### PM L2

PM L2 owns phase authority, approved scope, forbidden scope, shared-file locks, merge authority, and server-apply authority. PM L2 is the only default merge authority.

### PM L3

PM L3 owns delivery decomposition, Sub-chat routing, evidence validation, blocker classification, and return packaging for PM L2.

### Sub-chat roles

Sub-chat roles execute one assigned task inside the approved scope. Each Sub-chat starts with handoff intake, performs only the assigned work, and returns a normalized report with done, not done, blockers, and next step.

## Layers

### Contract layer

The contract layer defines Task, Handoff, RoleOutput, and AuditEvent schemas using JSON Schema Draft 2020-12.

### Flowise skeleton layer

The Flowise layer defines abstract orchestration and routing descriptors. These files have `status=skeleton_contract` and `runtime_claim=false`.

### State API contract stub

The State API file describes abstract entities and operations only. It has `status=contract_stub_only` and `runtime_claim=false`.

### Security policy

The security policy forbids secrets, credentials, private endpoints, and live deployment data in repository artifacts.

### CI validation

CI validates bootstrap contracts, YAML files, required files, no-secret expectations, and no positive runtime claim. CI does not deploy anything and does not prove production readiness.

## Source of Truth boundary

GitHub and repository history are the Source of Truth for architecture and code. Server state is Applied State only and is not architecture proof.

## Data flow

```text
task -> handoff -> role output -> audit event -> validation
```

1. A task records goal, scope, lane, execution mode, repository state, authority, acceptance criteria, and stop conditions.
2. A handoff transfers the role-specific context, verified state, scope, authority, and required return format.
3. A role output reports the normalized result.
4. An audit event records evidence and outcome.
5. Validation checks contracts, scope, and authority boundaries.

## Runtime status

Flowise descriptors are not deployed runtime artifacts. The State API contract stub is not an implemented service.
