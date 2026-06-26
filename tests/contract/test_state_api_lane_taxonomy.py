from __future__ import annotations

import json
import pathlib
from typing import Any

import yaml


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
FLOWISEAI_PM_LANE = "flowiseai_pm_orchestration"
LANE_SCHEMA_PATHS = [
    "contracts/schemas/task.schema.json",
    "contracts/schemas/handoff.schema.json",
    "contracts/schemas/role-output.schema.json",
    "contracts/schemas/audit-event.schema.json",
]


def load_json(path: str) -> dict[str, Any]:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def load_yaml(path: str) -> dict[str, Any]:
    data = yaml.safe_load((REPO_ROOT / path).read_text(encoding="utf-8"))
    assert isinstance(data, dict), path
    return data


def test_flowiseai_pm_lane_is_accepted_by_relevant_json_schema_enums() -> None:
    for path in LANE_SCHEMA_PATHS:
        schema = load_json(path)
        assert FLOWISEAI_PM_LANE in schema["properties"]["lane"]["enum"], path


def test_flowiseai_pm_lane_is_bound_in_execution_mapping() -> None:
    data = load_yaml("contracts/bindings/execution_mapping.yaml")
    assert FLOWISEAI_PM_LANE in data["lanes"]
    assert "flowiseai-pm/" in data["lanes"][FLOWISEAI_PM_LANE]["branch_prefixes"]


def test_state_api_contract_uses_flowiseai_pm_lane_taxonomy() -> None:
    task_schema = load_json("contracts/schemas/task.schema.json")
    assert FLOWISEAI_PM_LANE in task_schema["properties"]["lane"]["enum"]
