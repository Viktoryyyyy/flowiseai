from __future__ import annotations

from state_api.runtime.operations import StateApiOperations

from .config import UniversalRoleRunnerConfig
from .github_execution_requests import (
    build_github_execution_request,
    reject_github_execution_request_execution,
)
from .models import JsonDict, require_idempotency_key
from .persistence import (
    build_pm_l3_decision_role_output,
    build_role_output,
    role_output_to_state_api_payload,
)
from .schema_validation import (
    validate_github_execution_request,
    validate_pm_l3_decision,
    validate_role_output,
)
from .task_builders import role_task_to_state_api_task


class UniversalRoleRunner:
    """Narrow local/dev facade over existing StateApiOperations public methods."""

    def __init__(
        self,
        operations: StateApiOperations,
        config: UniversalRoleRunnerConfig | None = None,
    ) -> None:
        self.operations = operations
        self.config = config or UniversalRoleRunnerConfig()

    def create_role_task(self, role_task: JsonDict, *, idempotency_key: str) -> JsonDict:
        require_idempotency_key(idempotency_key, "create_role_task")
        return self.operations.create_task(
            role_task_to_state_api_task(role_task),
            idempotency_key=idempotency_key,
        )

    def read_role_task(self, role_task_id: str) -> JsonDict:
        return self.operations.read_task(role_task_id)

    def claim_next_role_task(
        self,
        *,
        lane: str,
        claimant_role: str | None = None,
        claimant_id: str | None = None,
        idempotency_key: str,
        lease_duration_seconds: int | None = None,
    ) -> JsonDict:
        require_idempotency_key(idempotency_key, "claim_next_role_task")
        return self.operations.claim_next_task(
            lane=lane,
            claimant_role=claimant_role or self.config.claimant_role,
            claimant_id=claimant_id or self.config.claimant_id,
            lease_duration_seconds=lease_duration_seconds,
            idempotency_key=idempotency_key,
        )

    def transition_role_task(
        self,
        role_task_id: str,
        target_state: str,
        *,
        idempotency_key: str,
        actor_role: str | None = None,
        reason: str | None = None,
    ) -> JsonDict:
        require_idempotency_key(idempotency_key, "transition_role_task")
        return self.operations.transition_task_state(
            role_task_id,
            target_state,
            idempotency_key=idempotency_key,
            actor_role=actor_role or self.config.claimant_role,
            reason=reason,
        )

    def persist_role_output(self, role_output: JsonDict, *, idempotency_key: str) -> JsonDict:
        require_idempotency_key(idempotency_key, "persist_role_output")
        validate_role_output(role_output)
        return self.operations.persist_role_output(
            role_output_to_state_api_payload(
                role_output,
                project=self.config.project,
                lane="flowiseai_pm_orchestration",
                execution_mode=self.config.execution_mode,
            ),
            idempotency_key=idempotency_key,
        )

    def build_pm_l3_decision_role_output(
        self,
        *,
        decision: JsonDict,
        role_task_id: str,
        role_output_id: str,
        created_at: str,
        evidence_refs: list[JsonDict] | None = None,
    ) -> JsonDict:
        validate_pm_l3_decision(decision)
        return build_pm_l3_decision_role_output(
            decision=decision,
            role_task_id=role_task_id,
            role_output_id=role_output_id,
            created_at=created_at,
            project=self.config.project,
            lane="flowiseai_pm_orchestration",
            execution_mode=self.config.execution_mode,
            evidence_refs=evidence_refs,
        )

    def persist_pm_l3_decision(
        self,
        decision: JsonDict,
        *,
        role_task_id: str,
        role_output_id: str,
        created_at: str,
        idempotency_key: str,
        evidence_refs: list[JsonDict] | None = None,
    ) -> JsonDict:
        require_idempotency_key(idempotency_key, "persist_pm_l3_decision")
        role_output = self.build_pm_l3_decision_role_output(
            decision=decision,
            role_task_id=role_task_id,
            role_output_id=role_output_id,
            created_at=created_at,
            evidence_refs=evidence_refs,
        )
        return self.persist_role_output(role_output, idempotency_key=idempotency_key)

    def build_github_execution_request(self, **kwargs: object) -> JsonDict:
        request = build_github_execution_request(**kwargs)  # type: ignore[arg-type]
        return validate_github_execution_request(request)

    def persist_github_execution_request(
        self,
        request: JsonDict,
        *,
        role_task_id: str,
        role_output_id: str,
        created_at: str,
        idempotency_key: str,
    ) -> JsonDict:
        require_idempotency_key(idempotency_key, "persist_github_execution_request")
        role_output = build_role_output(
            role_output_id=role_output_id,
            role_task_id=role_task_id,
            producing_role="UNIVERSAL_ROLE_RUNNER",
            output_type="evidence_report",
            payload={
                "artifact_type": "github_execution_request",
                "github_execution_request": validate_github_execution_request(request),
            },
            created_at=created_at,
            project=self.config.project,
            lane="flowiseai_pm_orchestration",
            execution_mode=self.config.execution_mode,
        )
        return self.persist_role_output(role_output, idempotency_key=idempotency_key)

    def reject_github_execution_request(self, request: JsonDict, *, attempted_action: str = "execute") -> None:
        reject_github_execution_request_execution(request, attempted_action=attempted_action)