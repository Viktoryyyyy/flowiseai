from __future__ import annotations

import pathlib
import re
from typing import Any

import yaml


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

YAML_FILES = {
    "pm_l2_flow": "docs/pm_l2_flow_tz.yaml",
    "execution_mapping": "contracts/bindings/execution_mapping.yaml",
    "state_api": "state_api/runtime_stub/state_api_contract.yaml",
    "workflow": ".github/workflows/tests.yml",
}

ALLOWED_PLACEHOLDER_VALUES = {"none", "not_applicable", "<REDACTED>", "<SECRET_FROM_ENV>", "${ENV_VAR_NAME}"}


def load_yaml(path: str) -> dict[str, Any]:
    with (REPO_ROOT / path).open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    assert isinstance(data, dict), path
    return data


def walk_strings(value: Any) -> list[str]:
    if isinstance(value, dict):
        result: list[str] = []
        for item in value.values():
            result.extend(walk_strings(item))
        return result
    if isinstance(value, list):
        result = []
        for item in value:
            result.extend(walk_strings(item))
        return result
    if isinstance(value, str):
        return [value]
    return []


def assert_no_secret_like_values(data: dict[str, Any], path: str) -> None:
    patterns = [
        re.compile(r"AKIA[0-9A-Z]{16}"),
        re.compile(r"ghp_[A-Za-z0-9_]{20,}"),
        re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
        re.compile(r"sk-[A-Za-z0-9]{20,}"),
    ]
    for value in walk_strings(data):
        for pattern in patterns:
            assert not pattern.search(value), path

    def inspect_mapping(mapping: Any) -> None:
        if isinstance(mapping, dict):
            for key, value in mapping.items():
                key_text = str(key).lower()
                if any(marker in key_text for marker in ["secret", "token", "api_key", "password", "credential"]):
                    assert str(value) in ALLOWED_PLACEHOLDER_VALUES, f"{path}:{key}"
                inspect_mapping(value)
        elif isinstance(mapping, list):
            for item in mapping:
                inspect_mapping(item)

    inspect_mapping(data)


def assert_no_live_url_values(data: dict[str, Any], path: str) -> None:
    for value in walk_strings(data):
        assert "http://" not in value
        assert "https://" not in value


def test_yaml_files_parse() -> None:
    for path in YAML_FILES.values():
        load_yaml(path)


def test_pm_l2_flow_required_top_level_keys() -> None:
    data = load_yaml(YAML_FILES["pm_l2_flow"])
    for key in [
        "schema_version",
        "system_name",
        "phase",
        "repository_full_name",
        "base_ref",
        "base_sha",
        "lane",
        "execution_mode",
        "roles",
        "role_sequence",
        "allowed_transitions",
        "validation_gates",
        "authority_boundary",
        "shared_file_lock",
        "artifact_outputs",
    ]:
        assert key in data

    assert data["lane"] == "integration"
    assert data["execution_mode"] == "browser_chatgpt_github_direct"
    assert data["authority_boundary"]["merge_authority"] == "PM_L2_ONLY"
    assert data["authority_boundary"]["direct_main_write_allowed"] is False
    assert data["authority_boundary"]["allowed_branch"].startswith("integration/")


def test_execution_mapping_required_top_level_keys() -> None:
    data = load_yaml(YAML_FILES["execution_mapping"])
    for key in [
        "schema_version",
        "roles",
        "lanes",
        "execution_modes",
        "role_outputs",
        "schema_refs",
        "validators",
        "authority_boundaries",
        "forbidden_action_classes",
    ]:
        assert key in data

    assert data["role_outputs"]["SUBCHAT_SPEC_CONTRACT_DESIGNER"] == "spec_package"
    assert data["role_outputs"]["SUBCHAT_IMPLEMENTATION"] == "implementation_report"
    assert data["role_outputs"]["SUBCHAT_VALIDATION"] == "validation_report"
    assert "integration/" in data["lanes"]["integration"]["branch_prefixes"]
    assert data["authority_boundaries"]["merge_authority"] == "PM_L2_ONLY"


def test_state_api_is_contract_stub_only() -> None:
    data = load_yaml(YAML_FILES["state_api"])
    for key in [
        "schema_version",
        "status",
        "runtime_claim",
        "entities",
        "abstract_operations",
        "state_enums",
        "schema_refs",
        "runtime_boundary",
    ]:
        assert key in data

    assert data["status"] == "contract_stub_only"
    assert data["runtime_claim"] is False
    assert set(["Task", "Handoff", "RoleOutput", "AuditEvent", "StateSnapshot"]).issubset(data["entities"])
    assert "created" in data["state_enums"]
    assert data["runtime_boundary"]["server_url"] == "none"


def test_workflow_contract() -> None:
    data = load_yaml(YAML_FILES["workflow"])
    trigger = data.get("on", data.get(True))
    assert data["name"] == "tests"
    assert "pull_request" in trigger
    assert "jobs" in data
    text = (REPO_ROOT / YAML_FILES["workflow"]).read_text(encoding="utf-8").lower()
    for forbidden in ["server apply", "runtime smoke"]:
        assert forbidden not in text
    assert "pytest tests/contract/test_json_schemas.py" in text
    assert "pytest tests/contract/test_yaml_contracts.py" in text
    assert "pytest tests/contract/test_required_bootstrap_files.py" in text


def test_yaml_files_have_no_secret_values_or_live_urls() -> None:
    for path in YAML_FILES.values():
        data = load_yaml(path)
        assert_no_secret_like_values(data, path)
        assert_no_live_url_values(data, path)
