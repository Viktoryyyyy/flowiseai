from __future__ import annotations

import copy
from datetime import datetime, timezone
from typing import Callable

from .audit import build_audit_event
from .config import RuntimeConfig
from .errors import LeaseError, NotFoundError, RuntimeValidationError
from .idempotency import execute_idempotent
from .leases import build_lease, parse_utc_iso, release_lease_payload, renew_lease_payload, utc_iso
from .models import ALLOWED_TRANSITIONS, DEFAULT_BACKOFF_SECONDS, DEFAULT_MAX_ATTEMPTS, JsonDict, STATE_API_SCHEMA_VERSION
from .persistence import SQLiteStateRepository
from .snapshots import build_state_snapshot
from .validation import ensure_object, require_non_empty_string, validate_transition


class StateApiOperations:
    """Minimal local/dev State API runtime operations."""

    def __init__(
        self,
        repository: SQLiteStateRepository,
        config: RuntimeConfig | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self.repository = repository
        self.config = config or RuntimeConfig(sqlite_path=repository.sqlite_path)
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def _now_iso(self) -> str:
        return utc_iso(self.clock())

    @staticmethod
    def _actor_from_task(task: JsonDict) -> str:
        value = task.get("assigned_role")
        return value if isinstance(value, str) and value else "STATE_API_RUNTIME"

    def _insert_runtime_audit(
        self,
        *,
        task: JsonDict | None,
        operation_name: str,
        event_type: str,
        actor_role: str,
        now_iso: str,
        outcome: str,
        subject_ref: JsonDict | None = None,
        evidence_ref: JsonDict | None = None,
        state_transition: JsonDict | None = None,
        idempotency_key: str | None = None,
        lease_ref: str | None = None,
    ) -> None:
        self.repository.insert_audit_event(
            build_audit_event(
                task=task,
                operation_name=operation_name,
                event_type=event_type,
                actor_role=actor_role,
                occurred_at=now_iso,
                outcome=outcome,
                subject_ref=subject_ref,
                evidence_ref=evidence_ref,
                state_transition=state_transition,
                idempotency_key=idempotency_key,
                lease_ref=lease_ref,
            )
        )

    def create_task(self, task: JsonDict, idempotency_key: str | None) -> JsonDict:
        operation_name = "create_task"
        task_payload = copy.deepcopy(ensure_object(task, "task"))
        require_non_empty_string(task_payload, "task_id")
        now_iso = self._now_iso()
        request_payload = {"task": task_payload}

        def action() -> JsonDict:
            task_to_store = copy.deepcopy(task_payload)
            task_to_store.setdefault("lifecycle_state", "created")
            task_to_store.setdefault(
                "retry_failure_metadata",
                {
                    "attempt_count": 0,
                    "max_attempts": DEFAULT_MAX_ATTEMPTS,
                    "retry_state": "not_retryable",
                    "failure_state": "none",
                    "next_retry_after": None,
                    "backoff_policy_ref": f"default:{DEFAULT_BACKOFF_SECONDS}",
                },
            )
            self.repository.insert_task(task_to_store, now_iso)
            self._insert_runtime_audit(
                task=task_to_store,
                operation_name=operation_name,
                event_type="task_created",
                actor_role=self._actor_from_task(task_to_store),
                now_iso=now_iso,
                outcome="task persisted",
                subject_ref={"task_id": task_to_store["task_id"]},
                idempotency_key=idempotency_key,
            )
            return {"task_ref": task_to_store["task_id"], "task": task_to_store}

        return execute_idempotent(
            repository=self.repository,
            operation_name=operation_name,
            idempotency_key=idempotency_key,
            request_payload=request_payload,
            now_iso=now_iso,
            action=action,
        )

    def read_task(self, task_id: str) -> JsonDict:
        task = self.repository.get_task(task_id)
        if task is None:
            raise NotFoundError("Task", task_id)
        return {"task": task}

    def transition_task_state(
        self,
        task_id: str,
        target_state: str,
        idempotency_key: str | None,
        actor_role: str = "STATE_API_RUNTIME",
        reason: str | None = None,
    ) -> JsonDict:
        operation_name = "transition_task_state"
        now_iso = self._now_iso()
        request_payload = {
            "task_id": task_id,
            "target_state": target_state,
            "actor_role": actor_role,
            "reason": reason,
        }

        def action() -> JsonDict:
            task = self.repository.get_task(task_id)
            if task is None:
                raise NotFoundError("Task", task_id)
            from_state = str(task.get("lifecycle_state", "created"))
            validate_transition(from_state, target_state)
            task = copy.deepcopy(task)
            task["lifecycle_state"] = target_state
            task.setdefault("metadata", {}).setdefault("extensions", {})["last_transition_reason"] = reason or ""
            self.repository.update_task(task, now_iso)
            transition = {
                "transition_id": f"transition-{task_id}-{from_state}-{target_state}-{now_iso}",
                "schema_version": STATE_API_SCHEMA_VERSION,
                "task_id": task_id,
                "from_state": from_state,
                "to_state": target_state,
                "actor_role": actor_role,
                "occurred_at": now_iso,
                "reason": reason or "",
                "allowed_transitions": ALLOWED_TRANSITIONS,
                "terminal_states": ["validated", "failed"],
                "runtime_claim": False,
            }
            self._insert_runtime_audit(
                task=task,
                operation_name=operation_name,
                event_type="task_state_transitioned",
                actor_role=actor_role,
                now_iso=now_iso,
                outcome="task state transitioned",
                subject_ref={"task_id": task_id},
                state_transition={
                    "from_state": from_state,
                    "to_state": target_state,
                    "allowed": True,
                    "transition_ref": transition["transition_id"],
                },
                idempotency_key=idempotency_key,
            )
            return {"task_id": task_id, "state_transition": transition, "task": task}

        return execute_idempotent(
            repository=self.repository,
            operation_name=operation_name,
            idempotency_key=idempotency_key,
            request_payload=request_payload,
            now_iso=now_iso,
            action=action,
        )

    def claim_next_task(
        self,
        lane: str,
        claimant_role: str,
        claimant_id: str,
        idempotency_key: str | None,
        lease_duration_seconds: int | None = None,
    ) -> JsonDict:
        operation_name = "claim_next_task"
        now_iso = self._now_iso()
        request_payload = {
            "lane": lane,
            "claimant_role": claimant_role,
            "claimant_id": claimant_id,
            "lease_duration_seconds": lease_duration_seconds,
        }

        def action() -> JsonDict:
            self.repository.expire_active_leases(now_iso)
            task = self.repository.find_claimable_task(lane, now_iso)
            if task is None:
                return {"lease": None}
            lease = build_lease(
                task_id=str(task["task_id"]),
                claimant_role=claimant_role,
                claimant_id=claimant_id,
                claimed_at=now_iso,
                lease_duration_seconds=lease_duration_seconds,
                max_lease_duration_seconds=self.config.max_lease_duration_seconds,
                default_lease_duration_seconds=self.config.lease_duration_seconds,
            )
            self.repository.insert_lease(lease)
            self._insert_runtime_audit(
                task=task,
                operation_name=operation_name,
                event_type="task_claimed",
                actor_role=claimant_role,
                now_iso=now_iso,
                outcome="task lease claimed",
                subject_ref={"task_id": task["task_id"]},
                lease_ref=lease["lease_id"],
                idempotency_key=idempotency_key,
            )
            return {"lease": lease}

        return execute_idempotent(
            repository=self.repository,
            operation_name=operation_name,
            idempotency_key=idempotency_key,
            request_payload=request_payload,
            now_iso=now_iso,
            action=action,
        )

    def renew_task_lease(
        self,
        lease_id: str,
        idempotency_key: str | None,
        claimant_id: str | None = None,
        lease_duration_seconds: int | None = None,
    ) -> JsonDict:
        operation_name = "renew_task_lease"
        now_iso = self._now_iso()
        request_payload = {
            "lease_id": lease_id,
            "claimant_id": claimant_id,
            "lease_duration_seconds": lease_duration_seconds,
        }

        def action() -> JsonDict:
            lease = self.repository.get_lease(lease_id)
            if lease is None:
                raise NotFoundError("TaskClaimLease", lease_id)
            if lease["lease_state"] not in {"active", "renewed"}:
                raise LeaseError("lease is not active", {"lease_id": lease_id, "lease_state": lease["lease_state"]})
            if parse_utc_iso(str(lease["expires_at"])) <= parse_utc_iso(now_iso):
                lease["lease_state"] = "expired"
                self.repository.update_lease(lease)
                raise LeaseError("lease is expired", {"lease_id": lease_id})
            if claimant_id is not None and lease.get("claimant_id") != claimant_id:
                raise LeaseError("lease claimant does not match", {"lease_id": lease_id})
            renewed = renew_lease_payload(
                lease=lease,
                renewed_at=now_iso,
                lease_duration_seconds=lease_duration_seconds,
                max_lease_duration_seconds=self.config.max_lease_duration_seconds,
                default_lease_duration_seconds=self.config.lease_duration_seconds,
            )
            self.repository.update_lease(renewed)
            task = self.repository.get_task(str(renewed["task_id"]))
            self._insert_runtime_audit(
                task=task,
                operation_name=operation_name,
                event_type="task_lease_renewed",
                actor_role=str(renewed["claimant_role"]),
                now_iso=now_iso,
                outcome="task lease renewed",
                subject_ref={"task_id": renewed["task_id"]},
                lease_ref=lease_id,
                idempotency_key=idempotency_key,
            )
            return {"task_id": str(renewed["task_id"]), "lease": renewed}

        return execute_idempotent(
            repository=self.repository,
            operation_name=operation_name,
            idempotency_key=idempotency_key,
            request_payload=request_payload,
            now_iso=now_iso,
            action=action,
        )

    def release_task_lease(
        self,
        lease_id: str,
        idempotency_key: str | None,
        claimant_id: str | None = None,
    ) -> JsonDict:
        operation_name = "release_task_lease"
        now_iso = self._now_iso()
        request_payload = {"lease_id": lease_id, "claimant_id": claimant_id}

        def persist_expired_lease_if_needed() -> None:
            latest = self.repository.get_lease(lease_id)
            if latest is None or latest["lease_state"] not in {"active", "renewed"}:
                return
            if parse_utc_iso(str(latest["expires_at"])) <= parse_utc_iso(now_iso):
                expired = copy.deepcopy(latest)
                expired["lease_state"] = "expired"
                self.repository.update_lease(expired)

        def action() -> JsonDict:
            lease = self.repository.get_lease(lease_id)
            if lease is None:
                raise NotFoundError("TaskClaimLease", lease_id)
            if lease["lease_state"] not in {"active", "renewed"}:
                raise LeaseError("lease is not active", {"lease_id": lease_id, "lease_state": lease["lease_state"]})
            if parse_utc_iso(str(lease["expires_at"])) <= parse_utc_iso(now_iso):
                lease["lease_state"] = "expired"
                self.repository.update_lease(lease)
                raise LeaseError("lease is expired", {"lease_id": lease_id})
            if claimant_id is not None and lease.get("claimant_id") != claimant_id:
                raise LeaseError("lease claimant does not match", {"lease_id": lease_id})
            released = release_lease_payload(lease=lease, released_at=now_iso)
            self.repository.update_lease(released)
            task = self.repository.get_task(str(released["task_id"]))
            self._insert_runtime_audit(
                task=task,
                operation_name=operation_name,
                event_type="task_lease_released",
                actor_role=str(released["claimant_role"]),
                now_iso=now_iso,
                outcome="task lease released",
                subject_ref={"task_id": released["task_id"]},
                lease_ref=lease_id,
                idempotency_key=idempotency_key,
            )
            return {"task_id": str(released["task_id"]), "lease": released}

        try:
            return execute_idempotent(
                repository=self.repository,
                operation_name=operation_name,
                idempotency_key=idempotency_key,
                request_payload=request_payload,
                now_iso=now_iso,
                action=action,
            )
        except LeaseError:
            persist_expired_lease_if_needed()
            raise

    def persist_handoff(self, handoff: JsonDict, idempotency_key: str | None) -> JsonDict:
        operation_name = "persist_handoff"
        handoff_payload = copy.deepcopy(ensure_object(handoff, "handoff"))
        handoff_id = require_non_empty_string(handoff_payload, "handoff_id")
        now_iso = self._now_iso()
        request_payload = {"handoff": handoff_payload}

        def action() -> JsonDict:
            self.repository.insert_handoff(handoff_payload)
            self._insert_runtime_audit(
                task=handoff_payload,
                operation_name=operation_name,
                event_type="handoff_persisted",
                actor_role=str(handoff_payload.get("from_role", "STATE_API_RUNTIME")),
                now_iso=now_iso,
                outcome="handoff persisted",
                subject_ref={"handoff_id": handoff_id},
                idempotency_key=idempotency_key,
            )
            return {"handoff_ref": handoff_id, "handoff": handoff_payload}

        return execute_idempotent(
            repository=self.repository,
            operation_name=operation_name,
            idempotency_key=idempotency_key,
            request_payload=request_payload,
            now_iso=now_iso,
            action=action,
        )

    def persist_role_output(self, role_output: JsonDict, idempotency_key: str | None) -> JsonDict:
        operation_name = "persist_role_output"
        role_output_payload = copy.deepcopy(ensure_object(role_output, "role_output"))
        require_non_empty_string(role_output_payload, "task_id")
        now_iso = self._now_iso()
        request_payload = {"role_output": role_output_payload}

        def action() -> JsonDict:
            role_output_ref = self.repository.insert_role_output(role_output_payload)
            self._insert_runtime_audit(
                task=role_output_payload,
                operation_name=operation_name,
                event_type="role_output_persisted",
                actor_role=str(role_output_payload.get("role", "STATE_API_RUNTIME")),
                now_iso=now_iso,
                outcome="role output persisted",
                subject_ref={"role_output_id": role_output_ref},
                idempotency_key=idempotency_key,
            )
            return {"role_output_ref": role_output_ref, "role_output": role_output_payload}

        return execute_idempotent(
            repository=self.repository,
            operation_name=operation_name,
            idempotency_key=idempotency_key,
            request_payload=request_payload,
            now_iso=now_iso,
            action=action,
        )

    def append_audit_event(self, audit_event: JsonDict, idempotency_key: str | None) -> JsonDict:
        operation_name = "append_audit_event"
        audit_event_payload = copy.deepcopy(ensure_object(audit_event, "audit_event"))
        event_id = require_non_empty_string(audit_event_payload, "event_id")
        audit_event_payload.setdefault("append_only", True)
        now_iso = self._now_iso()
        request_payload = {"audit_event": audit_event_payload}

        def action() -> JsonDict:
            self.repository.insert_audit_event(audit_event_payload)
            return {"audit_event_ref": event_id, "audit_event": audit_event_payload}

        return execute_idempotent(
            repository=self.repository,
            operation_name=operation_name,
            idempotency_key=idempotency_key,
            request_payload=request_payload,
            now_iso=now_iso,
            action=action,
        )

    def read_state_snapshot(
        self,
        project: str | None = None,
        lane: str | None = None,
        execution_mode: str | None = None,
    ) -> JsonDict:
        now_iso = self._now_iso()
        return {
            "state_snapshot": build_state_snapshot(
                repository=self.repository,
                generated_at=now_iso,
                project=project,
                lane=lane,
                execution_mode=execution_mode,
            )
        }
