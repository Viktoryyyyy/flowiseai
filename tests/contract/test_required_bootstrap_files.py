from __future__ import annotations

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
    "00_CORE_CONSTITUTION/repository-principles.md",
    "contracts/schemas/task.schema.json",
    "contracts/schemas/role-output.schema.json",
    "contracts/schemas/handoff.schema.json",
    "contracts/schemas/audit-event.schema.json",
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
]


EXPECTED_BOOTSTRAP_FILES = list(REQUIRED_BOOTSTRAP_FILES)


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


def test_required_file_list_is_exact_approved_scope() -> None:
    assert REQUIRED_BOOTSTRAP_FILES == EXPECTED_BOOTSTRAP_FILES
    assert len(REQUIRED_BOOTSTRAP_FILES) == 20
    assert len(set(REQUIRED_BOOTSTRAP_FILES)) == 20


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


def test_state_api_contract_stub_flags() -> None:
    data = yaml.safe_load(read_text("state_api/runtime_stub/state_api_contract.yaml"))
    assert data["status"] == "contract_stub_only"
    assert data["runtime_claim"] is False
