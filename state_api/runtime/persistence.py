from __future__ import annotations

from contextlib import contextmanager
import json
from pathlib import Path
import sqlite3
import threading
from typing import Any, Iterator

from .errors import ConflictError
from .models import JsonDict, LIFECYCLE_STATES


class SQLiteStateRepository:
    """SQLite local/dev repository boundary for the State API runtime MVP."""

    def __init__(self, sqlite_path: str = ":memory:") -> None:
        self.sqlite_path = sqlite_path
        self._lock = threading.RLock()
        self._transaction_depth = 0
        self._connection = sqlite3.connect(sqlite_path, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self.initialize()

    def close(self) -> None:
        self._connection.close()

    def initialize(self) -> None:
        migration_path = Path(__file__).resolve().parent / "migrations" / "0001_initial.sql"
        sql = migration_path.read_text(encoding="utf-8")
        with self._lock:
            self._connection.executescript(sql)
            self._connection.commit()

    @contextmanager
    def transaction(self) -> Iterator[None]:
        with self._lock:
            root_transaction = self._transaction_depth == 0
            if root_transaction:
                self._connection.execute("BEGIN IMMEDIATE")
            self._transaction_depth += 1
            try:
                yield
            except Exception:
                self._transaction_depth -= 1
                if root_transaction:
                    self._connection.rollback()
                raise
            else:
                self._transaction_depth -= 1
                if root_transaction:
                    self._connection.commit()

    def _commit_if_needed(self) -> None:
        if self._transaction_depth == 0:
            self._connection.commit()

    @staticmethod
    def _dumps(payload: JsonDict) -> str:
        return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

    @staticmethod
    def _loads(value: str) -> JsonDict:
        loaded = json.loads(value)
        assert isinstance(loaded, dict)
        return loaded

    def insert_task(self, payload: JsonDict, now_iso: str) -> None:
        task_id = str(payload["task_id"])
        lifecycle_state = str(payload.get("lifecycle_state", "created"))
        try:
            self._connection.execute(
                """
                INSERT INTO tasks(
                    task_id, project, lane, execution_mode, lifecycle_state,
                    created_at, updated_at, payload_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    task_id,
                    payload.get("project", ""),
                    payload.get("lane", ""),
                    payload.get("execution_mode", ""),
                    lifecycle_state,
                    payload.get("created_at", now_iso),
                    now_iso,
                    self._dumps(payload),
                ),
            )
            self._commit_if_needed()
        except sqlite3.IntegrityError as exc:
            raise ConflictError("task already exists", {"task_id": task_id}) from exc

    def get_task(self, task_id: str) -> JsonDict | None:
        row = self._connection.execute(
            "SELECT payload_json FROM tasks WHERE task_id = ?",
            (task_id,),
        ).fetchone()
        return None if row is None else self._loads(str(row["payload_json"]))

    def update_task(self, payload: JsonDict, now_iso: str) -> None:
        task_id = str(payload["task_id"])
        lifecycle_state = str(payload.get("lifecycle_state", "created"))
        self._connection.execute(
            """
            UPDATE tasks
            SET lifecycle_state = ?, updated_at = ?, payload_json = ?
            WHERE task_id = ?
            """,
            (lifecycle_state, now_iso, self._dumps(payload), task_id),
        )
        self._commit_if_needed()

    def find_claimable_task(self, lane: str, now_iso: str) -> JsonDict | None:
        row = self._connection.execute(
            """
            SELECT t.payload_json
            FROM tasks t
            WHERE t.lane = ?
              AND t.lifecycle_state IN ('created', 'assigned')
              AND NOT EXISTS (
                  SELECT 1
                  FROM task_claim_leases l
                  WHERE l.task_id = t.task_id
                    AND l.lease_state IN ('active', 'renewed')
                    AND l.expires_at > ?
              )
            ORDER BY t.created_at ASC, t.task_id ASC
            LIMIT 1
            """,
            (lane, now_iso),
        ).fetchone()
        return None if row is None else self._loads(str(row["payload_json"]))

    def insert_handoff(self, payload: JsonDict) -> None:
        handoff_id = str(payload["handoff_id"])
        try:
            self._connection.execute(
                """
                INSERT INTO handoffs(
                    handoff_id, task_id, project, lane, execution_mode, created_at, payload_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    handoff_id,
                    payload.get("task_id", ""),
                    payload.get("project", ""),
                    payload.get("lane", ""),
                    payload.get("execution_mode", ""),
                    payload.get("created_at", ""),
                    self._dumps(payload),
                ),
            )
            self._commit_if_needed()
        except sqlite3.IntegrityError as exc:
            raise ConflictError("handoff already exists", {"handoff_id": handoff_id}) from exc

    def get_handoff(self, handoff_id: str) -> JsonDict | None:
        row = self._connection.execute(
            "SELECT payload_json FROM handoffs WHERE handoff_id = ?",
            (handoff_id,),
        ).fetchone()
        return None if row is None else self._loads(str(row["payload_json"]))

    @staticmethod
    def role_output_id(payload: JsonDict) -> str:
        explicit = payload.get("role_output_id")
        if isinstance(explicit, str) and explicit:
            return explicit
        metadata = payload.get("metadata")
        if isinstance(metadata, dict):
            extensions = metadata.get("extensions")
            if isinstance(extensions, dict):
                metadata_id = extensions.get("role_output_id")
                if isinstance(metadata_id, str) and metadata_id:
                    return metadata_id
        return f"{payload.get('task_id', '')}:{payload.get('role', '')}:{payload.get('created_at', '')}"

    def insert_role_output(self, payload: JsonDict) -> str:
        role_output_id = self.role_output_id(payload)
        try:
            self._connection.execute(
                """
                INSERT INTO role_outputs(
                    role_output_id, task_id, project, lane, execution_mode, role, created_at, payload_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    role_output_id,
                    payload.get("task_id", ""),
                    payload.get("project", ""),
                    payload.get("lane", ""),
                    payload.get("execution_mode", ""),
                    payload.get("role", ""),
                    payload.get("created_at", ""),
                    self._dumps(payload),
                ),
            )
            self._commit_if_needed()
            return role_output_id
        except sqlite3.IntegrityError as exc:
            raise ConflictError(
                "role output is immutable; corrections require a new role output record",
                {"role_output_id": role_output_id},
            ) from exc

    def get_role_output(self, role_output_id: str) -> JsonDict | None:
        row = self._connection.execute(
            "SELECT payload_json FROM role_outputs WHERE role_output_id = ?",
            (role_output_id,),
        ).fetchone()
        return None if row is None else self._loads(str(row["payload_json"]))

    def insert_audit_event(self, payload: JsonDict) -> None:
        event_id = str(payload["event_id"])
        try:
            self._connection.execute(
                """
                INSERT INTO audit_events(
                    event_id, task_id, project, lane, execution_mode, event_type, occurred_at, payload_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event_id,
                    payload.get("task_id", ""),
                    payload.get("project", ""),
                    payload.get("lane", ""),
                    payload.get("execution_mode", ""),
                    payload.get("event_type", ""),
                    payload.get("occurred_at", ""),
                    self._dumps(payload),
                ),
            )
            self._commit_if_needed()
        except sqlite3.IntegrityError as exc:
            raise ConflictError("audit event already exists", {"event_id": event_id}) from exc

    def insert_lease(self, lease: JsonDict) -> None:
        self._connection.execute(
            """
            INSERT INTO task_claim_leases(
                lease_id, task_id, claimant_role, claimant_id, lease_state,
                claimed_at, expires_at, renewed_at, released_at,
                lease_duration_seconds, max_lease_duration_seconds,
                exclusive, runtime_claim, payload_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                lease["lease_id"],
                lease["task_id"],
                lease["claimant_role"],
                lease["claimant_id"],
                lease["lease_state"],
                lease["claimed_at"],
                lease["expires_at"],
                lease.get("renewed_at"),
                lease.get("released_at"),
                lease.get("lease_duration_seconds"),
                lease.get("max_lease_duration_seconds"),
                1 if lease.get("exclusive") is True else 0,
                1 if lease.get("runtime_claim") is True else 0,
                self._dumps(lease),
            ),
        )
        self._commit_if_needed()

    def get_lease(self, lease_id: str) -> JsonDict | None:
        row = self._connection.execute(
            "SELECT payload_json FROM task_claim_leases WHERE lease_id = ?",
            (lease_id,),
        ).fetchone()
        return None if row is None else self._loads(str(row["payload_json"]))

    def update_lease(self, lease: JsonDict) -> None:
        self._connection.execute(
            """
            UPDATE task_claim_leases
            SET lease_state = ?, expires_at = ?, renewed_at = ?, released_at = ?,
                lease_duration_seconds = ?, payload_json = ?
            WHERE lease_id = ?
            """,
            (
                lease["lease_state"],
                lease["expires_at"],
                lease.get("renewed_at"),
                lease.get("released_at"),
                lease.get("lease_duration_seconds"),
                self._dumps(lease),
                lease["lease_id"],
            ),
        )
        self._commit_if_needed()

    def expire_active_leases(self, now_iso: str) -> None:
        rows = self._connection.execute(
            """
            SELECT payload_json
            FROM task_claim_leases
            WHERE lease_state IN ('active', 'renewed')
              AND expires_at <= ?
            """,
            (now_iso,),
        ).fetchall()
        for row in rows:
            lease = self._loads(str(row["payload_json"]))
            lease["lease_state"] = "expired"
            self.update_lease(lease)
        self._commit_if_needed()

    def get_idempotency_record(self, operation_name: str, idempotency_key: str) -> JsonDict | None:
        row = self._connection.execute(
            """
            SELECT operation_name, idempotency_key, request_identity_hash, task_id,
                   status, result_json, error_json, created_at, completed_at
            FROM idempotency_records
            WHERE operation_name = ? AND idempotency_key = ?
            """,
            (operation_name, idempotency_key),
        ).fetchone()
        if row is None:
            return None
        return {
            "operation_name": row["operation_name"],
            "idempotency_key": row["idempotency_key"],
            "request_identity_hash": row["request_identity_hash"],
            "request_hash": row["request_identity_hash"],
            "task_id": row["task_id"],
            "status": row["status"],
            "result": None if row["result_json"] is None else self._loads(str(row["result_json"])),
            "error": None if row["error_json"] is None else self._loads(str(row["error_json"])),
            "created_at": row["created_at"],
            "completed_at": row["completed_at"],
            "runtime_claim": False,
        }

    def insert_idempotency_record(
        self,
        *,
        operation_name: str,
        idempotency_key: str,
        request_identity_hash: str,
        task_id: str,
        status: str,
        result: JsonDict | None,
        error: JsonDict | None,
        now_iso: str,
    ) -> None:
        self._connection.execute(
            """
            INSERT INTO idempotency_records(
                operation_name, idempotency_key, request_identity_hash,
                task_id, status, result_json, error_json, created_at, completed_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                operation_name,
                idempotency_key,
                request_identity_hash,
                task_id,
                status,
                None if result is None else self._dumps(result),
                None if error is None else self._dumps(error),
                now_iso,
                now_iso,
            ),
        )
        self._commit_if_needed()

    def task_state_counts(self, project: str | None = None, lane: str | None = None, execution_mode: str | None = None) -> dict[str, int]:
        query = "SELECT lifecycle_state, COUNT(*) AS count FROM tasks WHERE 1 = 1"
        params: list[Any] = []
        if project is not None:
            query += " AND project = ?"
            params.append(project)
        if lane is not None:
            query += " AND lane = ?"
            params.append(lane)
        if execution_mode is not None:
            query += " AND execution_mode = ?"
            params.append(execution_mode)
        query += " GROUP BY lifecycle_state"

        counts = {state: 0 for state in LIFECYCLE_STATES}
        for row in self._connection.execute(query, params).fetchall():
            counts[str(row["lifecycle_state"])] = int(row["count"])
        return counts

    def refs_for_table(
        self,
        table_name: str,
        id_column: str,
        project: str | None = None,
        lane: str | None = None,
        execution_mode: str | None = None,
    ) -> list[str]:
        if table_name not in {"tasks", "handoffs", "role_outputs", "audit_events"}:
            raise ValueError(f"unsupported table: {table_name}")
        if id_column not in {"task_id", "handoff_id", "role_output_id", "event_id"}:
            raise ValueError(f"unsupported id column: {id_column}")
        query = f"SELECT {id_column} AS ref FROM {table_name} WHERE 1 = 1"
        params: list[Any] = []
        if project is not None:
            query += " AND project = ?"
            params.append(project)
        if lane is not None:
            query += " AND lane = ?"
            params.append(lane)
        if execution_mode is not None:
            query += " AND execution_mode = ?"
            params.append(execution_mode)
        query += f" ORDER BY {id_column}"
        return [str(row["ref"]) for row in self._connection.execute(query, params).fetchall()]

    def active_lease_refs(self, project: str | None, lane: str | None, execution_mode: str | None, now_iso: str) -> list[str]:
        query = """
        SELECT l.lease_id
        FROM task_claim_leases l
        JOIN tasks t ON t.task_id = l.task_id
        WHERE l.lease_state IN ('active', 'renewed')
          AND l.expires_at > ?
        """
        params: list[Any] = [now_iso]
        if project is not None:
            query += " AND t.project = ?"
            params.append(project)
        if lane is not None:
            query += " AND t.lane = ?"
            params.append(lane)
        if execution_mode is not None:
            query += " AND t.execution_mode = ?"
            params.append(execution_mode)
        query += " ORDER BY l.lease_id"
        return [str(row["lease_id"]) for row in self._connection.execute(query, params).fetchall()]

    def count_rows(self, table_name: str) -> int:
        if table_name not in {
            "tasks",
            "handoffs",
            "role_outputs",
            "audit_events",
            "task_claim_leases",
            "idempotency_records",
        }:
            raise ValueError(f"unsupported table: {table_name}")
        row = self._connection.execute(f"SELECT COUNT(*) AS count FROM {table_name}").fetchone()
        return int(row["count"])
