from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .config import RuntimeConfig
from .errors import StateApiError
from .operations import StateApiOperations
from .persistence import SQLiteStateRepository


def create_app(config: RuntimeConfig | None = None) -> FastAPI:
    runtime_config = config or RuntimeConfig.from_env()
    repository = SQLiteStateRepository(runtime_config.sqlite_path)
    operations = StateApiOperations(repository, runtime_config)

    app = FastAPI(title="FlowiseAI PM State API Runtime MVP", version="0.1.0")
    app.state.repository = repository
    app.state.operations = operations

    @app.exception_handler(StateApiError)
    async def state_api_error_handler(_request: Request, exc: StateApiError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.code, "message": exc.message, "details": exc.details or {}}},
        )

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {
            "status": "ok",
            "runtime": "state_api_runtime_mvp",
            "auth_mode": runtime_config.auth_mode,
        }

    @app.post("/operations/create_task")
    async def create_task(payload: dict[str, Any]) -> dict[str, Any]:
        return operations.create_task(payload["task"], payload.get("idempotency_key"))

    @app.get("/operations/read_task/{task_id}")
    async def read_task(task_id: str) -> dict[str, Any]:
        return operations.read_task(task_id)

    @app.post("/operations/transition_task_state")
    async def transition_task_state(payload: dict[str, Any]) -> dict[str, Any]:
        return operations.transition_task_state(
            task_id=payload["task_id"],
            target_state=payload["target_state"],
            actor_role=payload.get("actor_role", "STATE_API_RUNTIME"),
            reason=payload.get("reason"),
            idempotency_key=payload.get("idempotency_key"),
        )

    @app.post("/operations/claim_next_task")
    async def claim_next_task(payload: dict[str, Any]) -> dict[str, Any]:
        return operations.claim_next_task(
            lane=payload["lane"],
            claimant_role=payload["claimant_role"],
            claimant_id=payload["claimant_id"],
            lease_duration_seconds=payload.get("lease_duration_seconds"),
            idempotency_key=payload.get("idempotency_key"),
        )

    @app.post("/operations/renew_task_lease")
    async def renew_task_lease(payload: dict[str, Any]) -> dict[str, Any]:
        return operations.renew_task_lease(
            lease_id=payload["lease_id"],
            claimant_id=payload.get("claimant_id"),
            lease_duration_seconds=payload.get("lease_duration_seconds"),
            idempotency_key=payload.get("idempotency_key"),
        )

    @app.post("/operations/release_task_lease")
    async def release_task_lease(payload: dict[str, Any]) -> dict[str, Any]:
        return operations.release_task_lease(
            lease_id=payload["lease_id"],
            claimant_id=payload.get("claimant_id"),
            idempotency_key=payload.get("idempotency_key"),
        )

    @app.post("/operations/persist_handoff")
    async def persist_handoff(payload: dict[str, Any]) -> dict[str, Any]:
        return operations.persist_handoff(payload["handoff"], payload.get("idempotency_key"))

    @app.post("/operations/persist_role_output")
    async def persist_role_output(payload: dict[str, Any]) -> dict[str, Any]:
        return operations.persist_role_output(payload["role_output"], payload.get("idempotency_key"))

    @app.post("/operations/append_audit_event")
    async def append_audit_event(payload: dict[str, Any]) -> dict[str, Any]:
        return operations.append_audit_event(payload["audit_event"], payload.get("idempotency_key"))

    @app.post("/operations/read_state_snapshot")
    async def read_state_snapshot(payload: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = payload or {}
        return operations.read_state_snapshot(
            project=payload.get("project"),
            lane=payload.get("lane"),
            execution_mode=payload.get("execution_mode"),
        )

    return app


app = create_app()
