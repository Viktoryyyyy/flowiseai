from __future__ import annotations

import json
import pathlib
import re
from typing import Any

from jsonschema import Draft202012Validator


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
SCHEMA_DIR = REPO_ROOT / "contracts" / "schemas"

REQUIRED_SCHEMA_FILES = [
    "task.schema.json",
    "role-output.schema.json",
    "handoff.schema.json",
    "audit-event.schema.json",
    "state-snapshot.schema.json",
    "task-lease.schema.json",
    "state-transition.schema.json",
    "idempotency-record.schema.json",
]

FLOWISEAI_PM_LANE = "flowiseai_pm_orchestration"


def load_schema(name: str) -> dict[str, Any]:
    with (SCHEMA_DIR / name).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def walk_values(value: Any) -> list[str]:
    if isinstance(value, dict):
        result: list[str] = []
        for item in value.values():
            result.extend(walk_values(item))
        return result
    if isinstance(value, list):
        result = []
        for item in value:
            result.extend(walk_values(item))
        return result
    if isinstance(value, str):
        return [value]
    return []


def assert_no_secret_like_values(schema: dict[str, Any], name: str) -> None:
    patterns = [
        re.compile(r"AKIA[0-9A-Z]{16}"),
        re.compile(r"ghp_[A-Za-z0-9_]{20,}"),
        re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
        re.compile(r"sk-[A-Za-z0-9]{20,}"),
    ]
    for value in walk_values(schema):
        for pattern in patterns:
            assert not pattern.search(value), name


def assert_no_live_url_values(schema: dict[str, Any], name: str) -> None:
    for value in walk_values(schema):
        if value.startswith("https://json-schema.org/"):
            continue
        assert "http://" not in value
        assert "https://" not in value


def test_required_schema_files_exist() -> None:
    for name in REQUIRED_SCHEMA_FILES:
        assert (SCHEMA_DIR / name).exists(), name


def test_all_json_schemas_validate_against_draft_2020_12() -> None:
    for path in SCHEMA_DIR.glob("*.schema.json"):
        schema = load_schema(path.name)
        assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
        Draft202012Validator.check_schema(schema)


def test_json_schemas_do_not_contain_secret_values_or_live_urls() -> None:
    for name in REQUIRED_SCHEMA_FILES:
        schema = load_schema(name)
        assert_no_secret_like_values(schema, name)
        assert_no_live_url_values(schema, name)


def test_minimal_task_instance_validates() -> None:
    schema = load_schema("task.schema.json")
    instance = {
        "contract_version": "1.0.0",
        "task_id": "flowiseai_phase_2a_state_api_contract_design_pr_v1",
        "project": "MOEX Bot",
        "lane": FLOWISEAI_PM_LANE,
        "execution_mode": "browser_chatgpt_github_direct",
        "repository_full_name": "Viktoryyyyy/flowiseai",
        "base_ref": "origin/main",
        "base_sha": "71feaf8bd12c85ffdbf6cee9c060963238238d7d",
        "branch_name": "flowiseai-pm/state-api-contract-design-v1",
        "assigned_role": "SUBCHAT_IMPLEMENTATION",
        "current_goal": "Create State API contract design package",
        "approved_file_scope": ["README.md"],
        "forbidden_file_scope": ["server apply"],
        "authority_boundary": {
            "merge_authority": "PM_L2_ONLY",
            "direct_main_write_allowed": False,
            "server_apply_authority": "NONE",
            "runtime_allowed": "no",
        },
        "acceptance_criteria": ["State API contract files exist"],
        "stop_conditions": ["scope change"],
        "created_at": "2026-06-26T00:00:00Z",
        "lifecycle_state": "created",
        "retry_failure_metadata": {
            "attempt_count": 0,
            "max_attempts": None,
            "retry_state": "not_retryable",
            "failure_state": "none",
            "next_retry_after": None,
            "backoff_policy_ref": None,
        },
        "metadata": {"extensions": {}},
    }
    Draft202012Validator(schema).validate(instance)


def test_minimal_role_output_instance_validates() -> None:
    schema = load_schema("role-output.schema.json")
    instance = {
        "output_version": "1.0.0",
        "role": "SUBCHAT_IMPLEMENTATION",
        "project": "MOEX Bot",
        "task_id": "flowiseai_phase_2a_state_api_contract_design_pr_v1",
        "lane": FLOWISEAI_PM_LANE,
        "execution_mode": "browser_chatgpt_github_direct",
        "status": "pass",
        "output_type": "implementation_report",
        "payload": {"branch_name": "flowiseai-pm/state-api-contract-design-v1"},
        "blockers": [],
        "role_step_report": {
            "alignment_with_root_task": "aligned",
            "done": ["created contract design files"],
            "not_done": ["merge"],
            "blockers": [],
            "next_step": "PM L3 validation",
        },
        "created_at": "2026-06-26T00:00:00Z",
        "immutable_persistence": {
            "required": True,
            "mutation_policy": "append_new_version_only",
            "replacement_policy": "forbidden",
        },
        "metadata": {"extensions": {}},
    }
    Draft202012Validator(schema).validate(instance)


def test_minimal_handoff_instance_validates() -> None:
    schema = load_schema("handoff.schema.json")
    instance = {
        "handoff_id": "FLOWISEAI-TEST-HANDOFF",
        "handoff_version": 1,
        "project": "MOEX Bot",
        "from_role": "PM_L3_DELIVERY_VALIDATION_OWNER",
        "to_role": "SUBCHAT_IMPLEMENTATION",
        "created_at": "2026-06-26T00:00:00Z",
        "root_task": "Create FlowiseAI PM orchestration system",
        "task_id": "flowiseai_phase_2a_state_api_contract_design_pr_v1",
        "lane": FLOWISEAI_PM_LANE,
        "execution_mode": "browser_chatgpt_github_direct",
        "current_goal": "Create approved State API contract design files",
        "verified_current_state": [{"fact": "main baseline checked", "proof": "commit sha"}],
        "relevant_repository_state": {"repository_full_name": "Viktoryyyyy/flowiseai"},
        "decisions_already_made": ["PR-first flow"],
        "approved_scope": ["README.md"],
        "forbidden_scope": ["server apply"],
        "shared_file_lock": {"required": True},
        "blockers": [],
        "unknowns": ["none"],
        "acceptance_criteria": ["files created"],
        "exact_task_for_receiver": "Implement approved scope",
        "required_first_checks": ["confirm target role"],
        "stop_conditions": ["scope changes"],
        "required_return_format": {"implementation_report": "required"},
        "authority_boundary": {
            "merge_authority": "PM_L2_ONLY",
            "direct_main_write_allowed": False,
            "server_apply_authority": "NONE",
            "runtime_allowed": "no",
        },
        "previous_role_report_summary": {
            "done": ["spec package"],
            "not_done": ["implementation"],
            "blockers": [],
        },
        "expiry_conditions": ["main changed"],
        "metadata": {"extensions": {}},
    }
    Draft202012Validator(schema).validate(instance)


def test_minimal_audit_event_instance_validates() -> None:
    schema = load_schema("audit-event.schema.json")
    instance = {
        "event_id": "audit-001",
        "schema_version": "1.0.0",
        "occurred_at": "2026-06-26T00:00:00Z",
        "project": "MOEX Bot",
        "task_id": "flowiseai_phase_2a_state_api_contract_design_pr_v1",
        "lane": FLOWISEAI_PM_LANE,
        "execution_mode": "browser_chatgpt_github_direct",
        "actor_role": "SUBCHAT_IMPLEMENTATION",
        "event_type": "task_state_transitioned",
        "operation_name": "transition_task_state",
        "subject_ref": {"task_id": "flowiseai_phase_2a_state_api_contract_design_pr_v1"},
        "evidence_ref": {"transition_contract": "contracts/schemas/state-transition.schema.json"},
        "outcome": "created to assigned transition accepted by contract",
        "redaction_state": "no_secret_payload",
        "append_only": True,
        "state_transition": {
            "from_state": "created",
            "to_state": "assigned",
            "allowed": True,
            "transition_ref": "transition-001",
        },
        "metadata": {"extensions": {}},
    }
    Draft202012Validator(schema).validate(instance)


def test_state_api_new_schema_instances_validate() -> None:
    instances = {
        "task-lease.schema.json": {
            "lease_id": "lease-001",
            "schema_version": "1.0.0",
            "task_id": "task-001",
            "claimant_role": "SUBCHAT_IMPLEMENTATION",
            "claimant_id": "worker-001",
            "lease_state": "active",
            "claimed_at": "2026-06-26T00:00:00Z",
            "expires_at": "2026-06-26T00:10:00Z",
            "lease_duration_seconds": None,
            "max_lease_duration_seconds": None,
            "exclusive": True,
            "runtime_claim": False,
        },
        "state-snapshot.schema.json": {
            "snapshot_id": "snapshot-001",
            "schema_version": "1.0.0",
            "project": "MOEX Bot",
            "lane": FLOWISEAI_PM_LANE,
            "execution_mode": "browser_chatgpt_github_direct",
            "generated_at": "2026-06-26T00:00:00Z",
            "read_only": True,
            "runtime_claim": False,
            "task_summary": {
                "task_refs": ["task-001"],
                "total_by_state": {
                    "created": 1,
                    "assigned": 0,
                    "running": 0,
                    "blocked": 0,
                    "completed": 0,
                    "validation_pending": 0,
                    "validated": 0,
                    "failed": 0,
                },
            },
            "handoff_summary": {"handoff_refs": ["handoff-001"]},
            "role_output_summary": {"role_output_refs": ["role-output-001"]},
            "audit_event_summary": {"audit_event_refs": ["audit-001"], "append_only": True},
            "lease_summary": {"active_lease_refs": ["lease-001"]},
        },
        "state-transition.schema.json": {
            "transition_id": "transition-001",
            "schema_version": "1.0.0",
            "task_id": "task-001",
            "from_state": "created",
            "to_state": "assigned",
            "actor_role": "PM_L3_DELIVERY_VALIDATION_OWNER",
            "occurred_at": "2026-06-26T00:00:00Z",
            "allowed_transitions": {
                "created": ["assigned", "blocked", "failed"],
                "assigned": ["running", "blocked", "failed"],
                "running": ["assigned", "blocked", "completed", "validation_pending", "failed"],
                "blocked": ["assigned", "failed"],
                "completed": ["validation_pending", "validated"],
                "validation_pending": ["validated", "blocked", "failed"],
                "validated": [],
                "failed": [],
            },
            "terminal_states": ["validated", "failed"],
            "runtime_claim": False,
        },
        "idempotency-record.schema.json": {
            "idempotency_key": "idem-001",
            "schema_version": "1.0.0",
            "operation_name": "create_task",
            "request_hash": "hash-001",
            "task_id": "task-001",
            "created_at": "2026-06-26T00:00:00Z",
            "completed_at": None,
            "status": "succeeded",
            "outcome_ref": {"task_ref": "task-001"},
            "runtime_claim": False,
        },
    }
    for schema_name, instance in instances.items():
        Draft202012Validator(load_schema(schema_name)).validate(instance)
