# CI Validation Scope

The `tests` workflow validates bootstrap-v1 contracts and the Phase 2A State API contract/design package.

## Validation included

CI checks:

- JSON Schema Draft 2020-12 syntax and metaschema validity;
- representative sample instances for task, handoff, role output, audit event, task lease, state snapshot, state transition, and idempotency record;
- YAML parsing and required top-level keys;
- required bootstrap and State API contract/design file presence and non-empty content;
- Flowise skeleton flags;
- State API contract-only flags;
- State API lifecycle transition contract;
- State API lane taxonomy contract for `flowiseai_pm_orchestration`;
- State API required operation contract;
- retry/failure representation through Task metadata plus AuditEvent only;
- no likely secret values;
- no live runtime endpoint values;
- no positive runtime claim.

## Validation excluded

CI does not deploy Flowise. CI does not implement or call the State API. CI does not perform server apply. CI does not perform runtime smoke.

A CI pass is evidence for PM review. It is not PM L2 merge approval and does not prove production readiness.
