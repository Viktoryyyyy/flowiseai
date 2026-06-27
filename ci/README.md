# CI Validation Scope

The `tests` workflow validates bootstrap-v1 contracts, the Phase 2A State API contract/design package, and the first local/dev State API runtime MVP.

## Validation included

CI checks:

- JSON Schema Draft 2020-12 syntax and metaschema validity;
- representative sample instances for task, handoff, role output, audit event, task lease, state snapshot, state transition, and idempotency record;
- YAML parsing and required top-level keys;
- required bootstrap and State API contract/design file presence and non-empty content;
- Flowise skeleton flags;
- State API contract-only flags for Phase 2A contract/stub files;
- State API lifecycle transition contract;
- State API lane taxonomy contract for `flowiseai_pm_orchestration`;
- State API required operation contract;
- retry/failure representation through Task metadata plus AuditEvent only;
- local/dev State API runtime tests under `tests/runtime`;
- SQLite local/dev persistence behavior through the repository layer;
- idempotency replay/conflict behavior;
- exclusive finite task lease behavior;
- append-only AuditEvent behavior;
- immutable RoleOutput behavior;
- read-only StateSnapshot behavior;
- no likely secret values;
- no live runtime endpoint values;
- no positive deployment or production runtime claim.

## Validation excluded

CI does not deploy Flowise. CI does not perform server apply. CI does not perform runtime smoke. CI does not validate a public endpoint, private endpoint, production database, production auth, monitoring, backup, rollback, Docker, systemd, nginx, TLS, or domain configuration.

A CI pass is evidence for PM review. It is not PM L2 merge approval and does not prove production readiness.
