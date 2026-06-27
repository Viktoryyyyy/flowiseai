CREATE TABLE IF NOT EXISTS tasks (
    task_id TEXT PRIMARY KEY,
    project TEXT NOT NULL,
    lane TEXT NOT NULL,
    execution_mode TEXT NOT NULL,
    lifecycle_state TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    payload_json TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_tasks_claimable
ON tasks(lane, lifecycle_state, created_at, task_id);

CREATE TABLE IF NOT EXISTS handoffs (
    handoff_id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    project TEXT NOT NULL,
    lane TEXT NOT NULL,
    execution_mode TEXT NOT NULL,
    created_at TEXT NOT NULL,
    payload_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS role_outputs (
    role_output_id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    project TEXT NOT NULL,
    lane TEXT NOT NULL,
    execution_mode TEXT NOT NULL,
    role TEXT NOT NULL,
    created_at TEXT NOT NULL,
    payload_json TEXT NOT NULL
);

CREATE TRIGGER IF NOT EXISTS role_outputs_no_update
BEFORE UPDATE ON role_outputs
BEGIN
    SELECT RAISE(ABORT, 'role_outputs immutable: update forbidden');
END;

CREATE TRIGGER IF NOT EXISTS role_outputs_no_delete
BEFORE DELETE ON role_outputs
BEGIN
    SELECT RAISE(ABORT, 'role_outputs immutable: delete forbidden');
END;

CREATE TABLE IF NOT EXISTS audit_events (
    event_id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    project TEXT NOT NULL,
    lane TEXT NOT NULL,
    execution_mode TEXT NOT NULL,
    event_type TEXT NOT NULL,
    occurred_at TEXT NOT NULL,
    payload_json TEXT NOT NULL
);

CREATE TRIGGER IF NOT EXISTS audit_events_no_update
BEFORE UPDATE ON audit_events
BEGIN
    SELECT RAISE(ABORT, 'audit_events append-only: update forbidden');
END;

CREATE TRIGGER IF NOT EXISTS audit_events_no_delete
BEFORE DELETE ON audit_events
BEGIN
    SELECT RAISE(ABORT, 'audit_events append-only: delete forbidden');
END;

CREATE TABLE IF NOT EXISTS task_claim_leases (
    lease_id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    claimant_role TEXT NOT NULL,
    claimant_id TEXT NOT NULL,
    lease_state TEXT NOT NULL,
    claimed_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    renewed_at TEXT,
    released_at TEXT,
    lease_duration_seconds INTEGER,
    max_lease_duration_seconds INTEGER,
    exclusive INTEGER NOT NULL,
    runtime_claim INTEGER NOT NULL,
    payload_json TEXT NOT NULL,
    FOREIGN KEY(task_id) REFERENCES tasks(task_id)
);

CREATE INDEX IF NOT EXISTS idx_task_claim_leases_active
ON task_claim_leases(task_id, lease_state, expires_at);

CREATE TABLE IF NOT EXISTS idempotency_records (
    operation_name TEXT NOT NULL,
    idempotency_key TEXT NOT NULL,
    request_identity_hash TEXT NOT NULL,
    task_id TEXT NOT NULL,
    status TEXT NOT NULL,
    result_json TEXT,
    error_json TEXT,
    created_at TEXT NOT NULL,
    completed_at TEXT,
    PRIMARY KEY(operation_name, idempotency_key)
);

CREATE INDEX IF NOT EXISTS idx_idempotency_records_task
ON idempotency_records(task_id);
