from __future__ import annotations

import importlib.util
import json
import pathlib
import re

import yaml


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

REQUIRED_BOOTSTRAP_FILES = [
    "README.md",
    "docs/bootstrap/system_bootstrap_v1.md",
    "docs/architecture-overview.md",
    "docs/pm_l2_flow_tz.yaml",
    "docs/state_api/state_api_minimal_design.md",
    "00_CORE_CONSTITUTION/repository-principles.md",
    "contracts/schemas/task.schema.json",
    "contracts/schemas/role-output.schema.json",
    "contracts/schemas/handoff.schema.json",
    "contracts/schemas/audit-event.schema.json",
    "contracts/schemas/state-snapshot.schema.json",
    "contracts/schemas/task-lease.schema.json",
    "contracts/schemas/state-transition.schema.json",
    "contracts/schemas/idempotency-record.schema.json",
    "contracts/bindings/execution_mapping.yaml",
    "flowise/orchestrator/root_flow.json",
    "flowise/orchestrator/router.json",
    "flowise/subchat/subchat_contract.json",
    "state_api/runtime_stub/state_api_contract.yaml",
    "security/credentials-policy.md",
    ".github/workflows/tests.yml",
    "ci/README.md",
    "tests/contract/test_json_schemas.py",
    "tests/contract/test_yaml_contracts.py",
    "tests/contract/test_required_bootstrap_files.py",
    "tests/contract/test_state_api_lifecycle_contract.py",
    "tests/contract/test_state_api_lane_taxonomy.py",
    "tests/contract/test_state_api_operation_contract.py"
]

EXPECTED_BOOTSTRAP_FILES = list(REQUIRED_BOOTSTRAP_FILES)

PHASE_12_APPROVED_FILE_SCOPE = [
    "docs/evidence/phase_10_hardening_controlled_run_001.md",
    "docs/orchestration/phase_12_live_github_execution_task.md",
    "tests/contract/test_required_bootstrap_files.py",
]

ALLOWED_PLACEHOLDERS = {
    "<REDACTED>",
    "<SECRET_FROM_ENV>",
    "${ENV_VAR_NAME}",
    "none",
    "not_applicable",
    "no_secret_payload",
    "redacted",
}

SECRET_VALUE_PATTERNS = [
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"ghp_[A-Za-z0-9_]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"BEGIN [A-Z ]*PRIVATE KEY"),
]

SENSITIVE_ASSIGNMENT = re.compile(
    r"(?i)\b(secret|token|api[_-]?key|password|credential)\b\s*[:=]\s*[\"']?([^\"'\n#]+)"
)


def read_text(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def has_forbidden_secret_value(text: str) -> bool:
    for pattern in SECRET_VALUE_PATTERNS:
        if pattern.search(text):
            return True

    for match in SENSITIVE_ASSIGNMENT.finditer(text):
        value = match.group(2).strip()
        if value and value not in ALLOWED_PLACEHOLDERS:
            if not value.startswith("<") and not value.startswith("${"):
                return True

    return False


def has_live_runtime_url(text: str) -> bool:
    url_pattern = re.compile(r"https?://[^\s)\"']+")
    allowed_prefixes = ("https://json-schema.org/",)
    for match in url_pattern.finditer(text):
        url = match.group(0)
        if not url.startswith(allowed_prefixes):
            return True
    return False


def has_positive_runtime_claim(text: str) -> bool:
    lowered = text.lower()
    blocked_phrases = [
        "runtime_claim" + "=" + "true",
        '"' + "runtime_claim" + '": ' + "true",
        "runtime_claim" + ": " + "true",
        "status" + "=" + "deployed",
        "status" + ": " + "deployed",
        " ".join(["flowise", "is", "deployed"]),
        " ".join(["state", "api", "is", "implemented"]),
        " ".join(["production", "is", "ready"]),
        " ".join(["runtime", "smoke", "passed"]),
    ]
    return any(phrase in lowered for phrase in blocked_phrases)


def load_contract_test_module(module_name: str):
    path = REPO_ROOT / "tests" / "contract" / f"{module_name}.py"
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def extract_yaml_block(text: str, marker: str) -> dict:
    marker_index = text.index(marker)
    block_start = text.rfind("```yaml", 0, marker_index)
    block_end = text.index("```", marker_index)
    assert block_start != -1
    yaml_text = text[block_start + len("```yaml"):block_end].strip()
    return yaml.safe_load(yaml_text)


def test_required_file_list_is_exact_approved_scope() -> None:
    assert REQUIRED_BOOTSTRAP_FILES == EXPECTED_BOOTSTRAP_FILES
    assert len(REQUIRED_BOOTSTRAP_FILES) == 28
    assert len(set(REQUIRED_BOOTSTRAP_FILES)) == 28


def test_every_required_file_exists_and_is_not_empty() -> None:
    for path in REQUIRED_BOOTSTRAP_FILES:
        full_path = REPO_ROOT / path
        assert full_path.exists(), path
        assert full_path.is_file(), path
        assert full_path.read_text(encoding="utf-8").strip(), path


def test_required_files_have_no_forbidden_secret_values_or_live_urls() -> None:
    for path in REQUIRED_BOOTSTRAP_FILES:
        text = read_text(path)
        assert not has_forbidden_secret_value(text), path
        assert not has_live_runtime_url(text), path


def test_required_files_have_no_positive_runtime_claim() -> None:
    for path in REQUIRED_BOOTSTRAP_FILES:
        assert not has_positive_runtime_claim(read_text(path)), path


def test_flowise_skeleton_files_are_contract_only() -> None:
    for path in [
        "flowise/orchestrator/root_flow.json",
        "flowise/orchestrator/router.json",
        "flowise/subchat/subchat_contract.json",
    ]:
        data = json.loads(read_text(path))
        assert data["status"] == "skeleton_contract"
        assert data["runtime_claim"] is False


def test_flowise_schema_references_exist() -> None:
    root_flow = json.loads(read_text("flowise/orchestrator/root_flow.json"))
    for schema_path in root_flow["schema_refs"].values():
        assert schema_path in REQUIRED_BOOTSTRAP_FILES
        assert (REPO_ROOT / schema_path).exists()


def test_state_api_contract_design_flags() -> None:
    data = yaml.safe_load(read_text("state_api/runtime_stub/state_api_contract.yaml"))
    assert data["status"] == "contract_only"
    assert data["runtime_claim"] is False
    assert data["implementation_status"] == "none"


def test_state_api_contract_design_modules_are_exercised_by_bootstrap_workflow() -> None:
    lifecycle = load_contract_test_module("test_state_api_lifecycle_contract")
    lifecycle.test_allowed_lifecycle_transitions_are_explicit_in_schema()
    lifecycle.test_allowed_lifecycle_transitions_are_explicit_in_yaml_contract()
    lifecycle.test_forbidden_transitions_are_not_listed()
    lifecycle.test_terminal_states_have_no_outgoing_transitions()

    lane = load_contract_test_module("test_state_api_lane_taxonomy")
    lane.test_flowiseai_pm_lane_is_accepted_by_relevant_json_schema_enums()
    lane.test_flowiseai_pm_lane_is_bound_in_execution_mapping()
    lane.test_state_api_contract_uses_flowiseai_pm_lane_taxonomy()

    operations = load_contract_test_module("test_state_api_operation_contract")
    operations.test_required_operations_are_represented_in_state_api_contract()
    operations.test_required_resources_and_schema_refs_are_represented()
    operations.test_mutating_operations_have_idempotency_contract()
    operations.test_state_api_contract_remains_runtime_neutral()
    operations.test_retry_representation_uses_task_metadata_plus_audit_event_only()


def test_phase10_hardening_evidence_artifact_preserves_required_identity() -> None:
    text = read_text("docs/evidence/phase_10_hardening_controlled_run_001.md")

    required_tokens = [
        "flowiseai_hardening_controlled_run_001",
        "corr-flowiseai-hardening-controlled-run-001-20260628",
        "flowise-run-request-hardening-controlled-run-001-20260628",
        "flowise-run-result-hardening-controlled-run-001-20260628",
        "flowiseai-hardening-controlled-run-001-20260628",
        "04c5238e-ab3a-4390-bd89-9cd137ced7e8",
        "6b217ffe57774473f841baef4a470d93227f5cf48814ec46b45d5323cd9282ff",
        "740fdc6c144ce93b5e6340e36c7de4aa82bae5983957492a1daad8ea1da5c8e4",
        "accepted_by_PM_L2",
        "clean_operational_loop: \"yes\"",
    ]

    for token in required_tokens:
        assert token in text


def test_phase12_task_records_flowise_blocker_and_direct_github_fallback() -> None:
    text = read_text("docs/orchestration/phase_12_live_github_execution_task.md")

    required_tokens = [
        "flowiseai_phase_12_live_github_execution_task",
        "corr-flowiseai-phase-12-live-github-execution-task-20260628",
        "flowise-run-request-phase-12-live-github-execution-task-20260628",
        "github_mutation_tool_unavailable_in_flowise_agent",
        "c999d23b42cf64b6b101ac7f0b4869d93356e5bce452e1ec443432aa6833d80f",
        "stale_phase_10_template_status: \"resolved\"",
        "github_direct_execution_required: true",
        "flowiseai-pm/phase-12-live-github-execution-task",
    ]

    for token in required_tokens:
        assert token in text


def test_canonical_phase10_artifact_remains_present_and_accepted() -> None:
    text = read_text("docs/orchestration/evidence/phase_10_controlled_run_2026-06-28.md")

    assert "# Phase 10 Controlled Run Evidence Package" in text
    assert "final_status: \"accepted_by_PM_L2\"" in text
    assert "execution_id: \"04c5238e-ab3a-4390-bd89-9cd137ced7e8\"" in text
    assert "graph_flowData_sha256: \"6b217ffe57774473f841baef4a470d93227f5cf48814ec46b45d5323cd9282ff\"" in text


def test_phase12_documents_approved_file_scope_exactly() -> None:
    text = read_text("docs/orchestration/phase_12_live_github_execution_task.md")
    approved_scope_block = extract_yaml_block(text, "approved_file_scope:")

    assert approved_scope_block["approved_file_scope"] == PHASE_12_APPROVED_FILE_SCOPE
    assert len(approved_scope_block["approved_file_scope"]) == len(PHASE_12_APPROVED_FILE_SCOPE)
    assert len(set(approved_scope_block["approved_file_scope"])) == len(PHASE_12_APPROVED_FILE_SCOPE)
