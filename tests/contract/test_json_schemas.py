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
]


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
        "task_id": "flowiseai_bootstrap_v1_implementation",
        "project": "MOEX Bot",
        "lane": "integration",
        "execution_mode": "browser_chatgpt_github_direct",
        "repository_full_name": "Viktoryyyyy/flowiseai",
        "base_ref": "origin/main",
        "base_sha": "255b537488084b3dbc10f777babda98a70ad979a",
        "branch_name": "integration/flowiseai-bootstrap-v1",
        "assigned_role": "SUBCHAT_IMPLEMENTATION",
        "current_goal": "Create bootstrap v1 contract files",
        "approved_file_scope": ["README.md"],
        "forbidden_file_scope": ["server apply"],
        "authority_boundary": {
            "merge_authority": "PM_L2_ONLY",
            "direct_main_write_allowed": False,
            "server_apply_authority": "NONE",
            "runtime_allowed": "no",
        },
        "acceptance_criteria": ["approved file exists"],
        "stop_conditions": ["scope change"],
        "created_at": "2026-06-26T00:00:00Z",
        "metadata": {"extensions": {}},
    }
    Draft202012Validator(schema).validate(instance)


def test_minimal_role_output_instance_validates() -> None:
    schema = load_schema("role-output.schema.json")
    instance = {
        "output_version": "1.0.0",
        "role": "SUBCHAT_IMPLEMENTATION",
        "project": "MOEX Bot",
        "task_id": "flowiseai_bootstrap_v1_implementation",
        "lane": "integration",
        "execution_mode": "browser_chatgpt_github_direct",
        "status": "pass",
        "output_type": "implementation_report",
        "payload": {"branch_name": "integration/flowiseai-bootstrap-v1"},
        "blockers": [],
        "role_step_report": {
            "alignment_with_root_task": "aligned",
            "done": ["created files"],
            "not_done": ["merge"],
            "blockers": [],
            "next_step": "PM L3 validation",
        },
        "created_at": "2026-06-26T00:00:00Z",
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
        "root_task": "Create FlowiseAI bootstrap v1",
        "task_id": "flowiseai_bootstrap_v1_implementation",
        "lane": "integration",
        "execution_mode": "browser_chatgpt_github_direct",
        "current_goal": "Create approved files",
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
        "task_id": "flowiseai_bootstrap_v1_implementation",
        "lane": "integration",
        "execution_mode": "browser_chatgpt_github_direct",
        "actor_role": "SUBCHAT_IMPLEMENTATION",
        "event_type": "implementation_committed",
        "subject_ref": {"branch": "integration/flowiseai-bootstrap-v1"},
        "evidence_ref": {"commit": "255b537488084b3dbc10f777babda98a70ad979a"},
        "outcome": "created approved bootstrap files",
        "redaction_state": "no_secret_payload",
        "metadata": {"extensions": {}},
    }
    Draft202012Validator(schema).validate(instance)
