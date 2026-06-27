# State API runtime MVP

This package is the first local/dev runtime implementation for the FlowiseAI PM State API.

Runtime boundary:

- FastAPI-style ASGI app object is provided for tests and local/dev use.
- SQLite persistence is local/dev only and isolated behind `SQLiteStateRepository`.
- No live server startup, public endpoint, private endpoint, deployment, Flowise deployment, server apply, or runtime smoke is included.
- Auth is `local_dev_no_auth` for this MVP only.
- No secrets, credentials, private URLs, or connection strings are required.

Implemented operations:

- `create_task`
- `read_task`
- `transition_task_state`
- `claim_next_task`
- `renew_task_lease`
- `release_task_lease`
- `persist_handoff`
- `persist_role_output`
- `append_audit_event`
- `read_state_snapshot`

Semantics:

- Mutating operations require an idempotency key.
- Idempotency is scoped by `operation_name + idempotency_key`.
- The runtime stores a deterministic request identity hash.
- Same operation/key/hash replays the stored outcome.
- Same operation/key with a different hash returns a conflict.
- Task lifecycle transitions follow the Phase 2A transition table.
- `validated` and `failed` are terminal states.
- `claim_next_task` only claims tasks in `created` or `assigned` and does not change task state.
- Lease default duration is 600 seconds; max duration is 3600 seconds.
- Runtime-created leases are exclusive and finite.
- Audit events are append-only.
- Role outputs are immutable after creation; corrections require a new record.
- State snapshots are read-only projections and are not persisted by `read_state_snapshot`.
- Retry/failure defaults are represented in Task metadata plus AuditEvent only: `max_attempts=3`, `backoff_seconds=60`.
