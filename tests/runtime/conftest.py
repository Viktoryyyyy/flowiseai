from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest

from state_api.runtime.config import RuntimeConfig
from state_api.runtime.operations import StateApiOperations
from state_api.runtime.persistence import SQLiteStateRepository


BASE_SHA = "ff5ff0c0401f1852dcddf5ed173f26d37d81c85b"


class MutableClock:
    def __init__(self) -> None:
        self.current = datetime(2026, 6, 27, 0, 0, 0, tzinfo=timezone.utc)

    def __call__(self) -> datetime:
        return self.current

    def advance(self, seconds: int) -> None:
        self.current = self.current + timedelta(seconds=seconds)


@pytest.fixture
def clock() -> MutableClock:
    return MutableClock()


@pytest.fixture
def repository(tmp_path: Path) -> SQLiteStateRepository:
    repo = SQLiteStateRepository(str(tmp_path / "state_api.sqlite3"))
    try:
        yield repo
    finally:
        repo.close()


@pytest.fixture
def operations(repository: SQLiteStateRepository, clock: MutableClock) -> StateApiOperations:
    return StateApiOperations(
        repository,
        RuntimeConfig(sqlite_path=repository.sqlite_path),
        clock=clock,
    )


def sample_task(task_id: str = "task-001", lifecycle_state: str = "created") -> dict[str, Any]:
    return {
        "contract_version": "1.0.0",
        "task_id": task_id,
        "project": "MOEX Bot",
        "lane": "flowiseai_pm_orchestration",
        "execution_mode": "browser_chatgpt_github_direct",
        "repository_full_name": "Viktoryyyyy/flowiseai",
        "base_ref": "main",
        "base_sha": BASE_SHA,
        "branch_name": "flowiseai/phase-2b-state-api-runtime-mvp-v1",
        "assigned_role": "SUBCHAT_IMPLEMENTATION",
        "current_goal": "Implement State API runtime MVP",
        "approved_file_scope": ["state_api/runtime/**", "tests/runtime/**"],
        "forbidden_file_scope": ["README.md", "contracts/schemas/*.json"],
        "authority_boundary": {
            "merge_authority": "PM_L2_ONLY",
            "direct_main_write_allowed": False,
            "server_apply_authority": "blocked_until_explicit_future_phase",
            "runtime_allowed": "no",
        },
        "acceptance_criteria": ["runtime tests pass"],
        "stop_conditions": ["scope widening required"],
        "created_at": "2026-06-27T00:00:00Z",
        "lifecycle_state": lifecycle_state,
    }


def sample_handoff(handoff_id: str = "handoff-001", task_id: str = "task-001") -> dict[str, Any]:
    return {
        "handoff_id": handoff_id,
        "handoff_version": 1,
        "project": "MOEX Bot",
        "from_role": "PM_L2_PHASE_OWNER",
        "to_role": "SUBCHAT_IMPLEMENTATION",
        "created_at": "2026-06-27T00:00:00Z",
        "root_task": "Create FlowiseAI PM orchestration system",
        "task_id": task_id,
        "lane": "flowiseai_pm_orchestration",
        "execution_mode": "browser_chatgpt_github_direct",
        "current_goal": "Implement runtime MVP",
        "verified_current_state": [{"fact": "Phase 2A accepted", "proof": "PR #3"}],
        "relevant_repository_state": {"repository_full_name": "Viktoryyyyy/flowiseai"},
        "decisions_already_made": ["Option A approved"],
        "approved_scope": ["state_api/runtime/**"],
        "forbidden_scope": ["deployment"],
        "shared_file_lock": {"required": True},
        "blockers": [],
        "unknowns": [],
        "acceptance_criteria": ["tests pass"],
        "exact_task_for_receiver": "Implement runtime",
        "required_first_checks": ["confirm role"],
        "stop_conditions": ["scope widening required"],
        "required_return_format": {"implementation_report": {}},
        "authority_boundary": {
            "merge_authority": "PM_L2_ONLY",
            "direct_main_write_allowed": False,
            "server_apply_authority": "blocked_until_explicit_future_phase",
            "runtime_allowed": "no",
        },
        "previous_role_report_summary": {"done": [], "not_done": [], "blockers": []},
        "expiry_conditions": ["main changed"],
    }


def sample_role_output(role_output_id: str = "role-output-001", task_id: str = "task-001") -> dict[str, Any]:
    return {
        "output_version": "1.0.0",
        "role": "SUBCHAT_IMPLEMENTATION",
        "project": "MOEX Bot",
        "task_id": task_id,
        "lane": "flowiseai_pm_orchestration",
        "execution_mode": "browser_chatgpt_github_direct",
        "status": "pass",
        "output_type": "implementation_report",
        "payload": {"result": "ok"},
        "blockers": [],
        "role_step_report": {
            "alignment_with_root_task": "aligned",
            "done": ["implemented"],
            "not_done": [],
            "blockers": [],
            "next_step": "PM L2 review",
        },
        "created_at": "2026-06-27T00:00:00Z",
        "immutable_persistence": {
            "required": True,
            "mutation_policy": "append_new_version_only",
            "replacement_policy": "forbidden",
        },
        "metadata": {"extensions": {"role_output_id": role_output_id}},
    }


def sample_audit_event(event_id: str = "audit-001", task_id: str = "task-001") -> dict[str, Any]:
    return {
        "event_id": event_id,
        "schema_version": "1.0.0",
        "occurred_at": "2026-06-27T00:00:00Z",
        "project": "MOEX Bot",
        "task_id": task_id,
        "lane": "flowiseai_pm_orchestration",
        "execution_mode": "browser_chatgpt_github_direct",
        "actor_role": "SUBCHAT_IMPLEMENTATION",
        "event_type": "audit_event_appended",
        "operation_name": "append_audit_event",
        "subject_ref": {"task_id": task_id},
        "evidence_ref": {},
        "outcome": "recorded",
        "redaction_state": "no_secret_payload",
        "append_only": True,
    }
