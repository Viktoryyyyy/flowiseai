from __future__ import annotations

from collections.abc import Callable

from .models import JsonDict, SchemaValidationError
from .runner import UniversalRoleRunner

RoleTaskHandler = Callable[[JsonDict], JsonDict]


class UniversalRoleRunnerExecutionLoop:
    """One-claim local/dev execution loop for UniversalRoleRunner.

    The loop deliberately executes only repository-local State API operations:
    claim, transition, read task, persist role output, and finish/fail the task.
    It does not call external models, Flowise, GitHub mutation APIs, server
    apply commands, deployments, or runtime smoke endpoints.
    """

    def __init__(
        self,
        runner: UniversalRoleRunner,
        *,
        lane: str = "flowiseai_pm_orchestration",
        claimant_role: str | None = None,
        claimant_id: str | None = None,
    ) -> None:
        self.runner = runner
        self.lane = lane
        self.claimant_role = claimant_role or runner.config.claimant_role
        self.claimant_id = claimant_id or runner.config.claimant_id

    @staticmethod
    def _require_prefix(value: str) -> str:
        if not isinstance(value, str) or not value:
            raise SchemaValidationError("idempotency key prefix is required")
        return value

    def _key(self, prefix: str, suffix: str) -> str:
        return f"{self._require_prefix(prefix)}:{suffix}"

    def _try_fail_task(self, task_id: str, *, prefix: str, reason: str) -> JsonDict | None:
        try:
            return self.runner.transition_role_task(
                task_id,
                "failed",
                idempotency_key=self._key(prefix, "failed"),
                actor_role=self.claimant_role,
                reason=reason,
            )
        except Exception:
            return None

    def run_once(
        self,
        handler: RoleTaskHandler,
        *,
        idempotency_key_prefix: str,
        lease_duration_seconds: int | None = None,
    ) -> JsonDict:
        """Claim at most one task and execute a supplied local handler.

        The handler receives the State API task payload and must return a
        RoleOutput-shaped payload accepted by UniversalRoleRunner.persist_role_output.
        """

        prefix = self._require_prefix(idempotency_key_prefix)
        claim = self.runner.claim_next_role_task(
            lane=self.lane,
            claimant_role=self.claimant_role,
            claimant_id=self.claimant_id,
            lease_duration_seconds=lease_duration_seconds,
            idempotency_key=self._key(prefix, "claim"),
        )
        lease = claim.get("lease")
        if lease is None:
            return {
                "status": "idle",
                "claimed": False,
                "task_id": None,
                "lease": None,
                "role_output_ref": None,
                "error": None,
            }

        task_id = str(lease["task_id"])
        try:
            assigned = self.runner.transition_role_task(
                task_id,
                "assigned",
                idempotency_key=self._key(prefix, "assigned"),
                actor_role=self.claimant_role,
                reason="claimed by UniversalRoleRunnerExecutionLoop",
            )
            running = self.runner.transition_role_task(
                task_id,
                "running",
                idempotency_key=self._key(prefix, "running"),
                actor_role=self.claimant_role,
                reason="handler execution started",
            )
            task = self.runner.read_role_task(task_id)["task"]
            role_output = handler(task)
            persisted = self.runner.persist_role_output(
                role_output,
                idempotency_key=self._key(prefix, "role_output"),
            )
            completed = self.runner.transition_role_task(
                task_id,
                "completed",
                idempotency_key=self._key(prefix, "completed"),
                actor_role=self.claimant_role,
                reason="handler output persisted",
            )
            return {
                "status": "completed",
                "claimed": True,
                "task_id": task_id,
                "lease": lease,
                "assigned_transition": assigned["state_transition"],
                "running_transition": running["state_transition"],
                "completed_transition": completed["state_transition"],
                "role_output_ref": persisted["role_output_ref"],
                "error": None,
            }
        except Exception as exc:
            failure_transition = self._try_fail_task(task_id, prefix=prefix, reason=str(exc))
            return {
                "status": "failed",
                "claimed": True,
                "task_id": task_id,
                "lease": lease,
                "role_output_ref": None,
                "error": {
                    "type": exc.__class__.__name__,
                    "message": str(exc),
                },
                "failure_transition": failure_transition["state_transition"] if failure_transition else None,
            }
