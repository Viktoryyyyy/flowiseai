from __future__ import annotations

import copy

from .models import JsonDict, SchemaValidationError


REQUIRED_EVIDENCE_KEYS = {
    "pr_evidence",
    "ci_evidence",
    "changed_files",
    "decision_trail",
    "blockers",
    "next_action",
    "final_pm_l2_evidence_package",
}


def _require_string(value: object, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise SchemaValidationError(f"{field} must be a non-empty string")
    return value


def aggregate_evidence_package(
    *,
    package_id: str,
    phase: str,
    repository_state: JsonDict,
    pr_evidence: list[JsonDict],
    ci_evidence: list[JsonDict],
    changed_files: list[str],
    decision_trail: list[JsonDict],
    blockers: list[JsonDict],
    next_action: str,
    created_at: str,
) -> JsonDict:
    """Aggregate repository-local orchestration evidence into one PM L2 package."""

    package: JsonDict = {
        "package_id": _require_string(package_id, "package_id"),
        "phase": _require_string(phase, "phase"),
        "project": "MOEX Bot",
        "lane": "flowiseai_pm_orchestration",
        "execution_mode": "browser_chatgpt_github_direct",
        "repository_state": copy.deepcopy(repository_state),
        "pr_evidence": copy.deepcopy(pr_evidence),
        "ci_evidence": copy.deepcopy(ci_evidence),
        "changed_files": list(changed_files),
        "decision_trail": copy.deepcopy(decision_trail),
        "blockers": copy.deepcopy(blockers),
        "next_action": _require_string(next_action, "next_action"),
        "server_deployment_status": {
            "server_apply": "not_performed",
            "deployment": "not_performed",
            "runtime_smoke": "not_performed",
            "flowise_install": "not_performed",
        },
        "forbidden_scope_compliance": {
            "server_files_changed": False,
            "deployment_files_changed": False,
            "secrets_changed": False,
            "private_endpoints_changed": False,
        },
        "created_at": _require_string(created_at, "created_at"),
    }
    package["final_pm_l2_evidence_package"] = {
        "phase": phase,
        "repository_state": package["repository_state"],
        "verified_prs_and_commits": package["pr_evidence"],
        "verified_ci_evidence": package["ci_evidence"],
        "changed_files_scope_summary": package["changed_files"],
        "decision_trail": package["decision_trail"],
        "blockers": package["blockers"],
        "server_deployment_status": package["server_deployment_status"],
        "recommended_next_authority_action": next_action,
    }
    missing = sorted(REQUIRED_EVIDENCE_KEYS - set(package))
    if missing:
        raise SchemaValidationError("evidence package missing required keys", {"missing": missing})
    return package


def evidence_package_is_decision_ready(package: JsonDict) -> bool:
    """Return true only when the package has PR, CI, changed-file, and decision evidence."""

    for key in REQUIRED_EVIDENCE_KEYS:
        if key not in package:
            return False
    if not package["pr_evidence"] or not package["ci_evidence"] or not package["changed_files"]:
        return False
    if package["blockers"]:
        return False
    return True
