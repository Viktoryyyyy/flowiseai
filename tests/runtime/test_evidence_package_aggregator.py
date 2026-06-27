from __future__ import annotations

from universal_role_runner.evidence_packages import aggregate_evidence_package, evidence_package_is_decision_ready


CREATED_AT = "2026-06-27T00:00:00Z"


def _package(blockers: list[dict] | None = None) -> dict:
    return aggregate_evidence_package(
        package_id="phase-3-evidence-package",
        phase="Phase 3",
        repository_state={"repository_full_name": "Viktoryyyyy/flowiseai", "main_sha": "abc"},
        pr_evidence=[{"pr_number": 11, "head_sha": "def", "merge_commit_sha": "ghi"}],
        ci_evidence=[{"workflow": "tests", "run_id": 1, "job_id": 2, "conclusion": "success"}],
        changed_files=["universal_role_runner/evidence_packages.py"],
        decision_trail=[{"decision_id": "decision-complete", "decision_type": "complete_phase_step"}],
        blockers=blockers or [],
        next_action="close Phase 3",
        created_at=CREATED_AT,
    )


def test_evidence_package_aggregator_builds_pm_l2_decision_package() -> None:
    package = _package()

    assert package["project"] == "MOEX Bot"
    assert package["server_deployment_status"] == {
        "server_apply": "not_performed",
        "deployment": "not_performed",
        "runtime_smoke": "not_performed",
        "flowise_install": "not_performed",
    }
    assert package["forbidden_scope_compliance"]["server_files_changed"] is False
    assert package["final_pm_l2_evidence_package"]["recommended_next_authority_action"] == "close Phase 3"
    assert evidence_package_is_decision_ready(package) is True


def test_evidence_package_with_blocker_is_not_decision_ready() -> None:
    package = _package(blockers=[{"code": "ci_failed", "message": "CI failed", "severity": "blocking"}])

    assert evidence_package_is_decision_ready(package) is False
