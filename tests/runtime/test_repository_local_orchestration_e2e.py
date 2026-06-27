from __future__ import annotations

from universal_role_runner import UniversalRoleRunner, build_role_output, build_role_task
from universal_role_runner.browser_handoffs import build_browser_handoff_block
from universal_role_runner.decision_routing import route_pm_l3_decision
from universal_role_runner.evidence_packages import aggregate_evidence_package, evidence_package_is_decision_ready
from universal_role_runner.execution_loop import UniversalRoleRunnerExecutionLoop


CREATED_AT = "2026-06-27T00:00:00Z"
BASE_SHA = "b44a98c3a8841e0e9d02ffb69e4f75a74bbe99af"


def _implementation_task() -> dict:
    return build_role_task(
        role_task_id="phase-3-e2e-implementation-task",
        phase_run_id="phase-run-3",
        lane="flowiseai_pm_orchestration",
        assigned_role="SUBCHAT_IMPLEMENTATION",
        approved_scope=["universal_role_runner/**", "tests/runtime/**", "docs/orchestration/**"],
        forbidden_scope=["server filesystem", "deployment", "secrets", "private endpoints"],
        acceptance_criteria=["repository-local orchestration e2e passes"],
        created_at=CREATED_AT,
        dynamic_context={"root_task": "Create FlowiseAI PM Orchestration system"},
    )


def _implementation_output(task_id: str) -> dict:
    return build_role_output(
        role_output_id="phase-3-e2e-implementation-output",
        role_task_id=task_id,
        producing_role="SUBCHAT_IMPLEMENTATION",
        output_type="implementation_report",
        payload={"status": "pass", "changed_files": ["universal_role_runner/browser_handoffs.py"]},
        created_at=CREATED_AT,
    )


def _validation_output(task_id: str) -> dict:
    return build_role_output(
        role_output_id="phase-3-e2e-validation-output",
        role_task_id=task_id,
        producing_role="SUBCHAT_VALIDATION",
        output_type="validation_report",
        payload={"validation_verdict": "pass", "repo_scope_check": "pass", "test_or_ci_check": "repo-local"},
        created_at=CREATED_AT,
    )


def test_repository_local_pm_orchestration_e2e_simulation(operations) -> None:
    runner = UniversalRoleRunner(operations)
    loop = UniversalRoleRunnerExecutionLoop(
        runner,
        claimant_role="SUBCHAT_IMPLEMENTATION",
        claimant_id="phase-3-e2e-worker",
    )
    runner.create_role_task(_implementation_task(), idempotency_key="phase-3-e2e-create-task")

    loop_result = loop.run_once(
        lambda task: _implementation_output(str(task["task_id"])),
        idempotency_key_prefix="phase-3-e2e-loop",
    )
    assert loop_result["status"] == "completed"

    validation_result = runner.persist_role_output(
        _validation_output("phase-3-e2e-implementation-task"),
        idempotency_key="phase-3-e2e-validation-output",
    )
    assert validation_result["role_output_ref"] == "phase-3-e2e-validation-output"

    decision = {
        "contract_version": "1.0.0",
        "decision_id": "phase-3-e2e-complete-step",
        "phase_run_id": "phase-run-3",
        "decision_type": "complete_phase_step",
        "next_role": None,
        "next_task": None,
        "routing_target": {"target_role": None, "target_queue": "none", "handoff_required": False},
        "acceptance_details": {"accepted": True, "criteria_met": ["implementation output persisted", "validation output persisted"]},
        "rejection_details": {"rejected": False, "reasons": []},
        "blocker_details": {"blocked": False, "blockers": []},
        "created_at": CREATED_AT,
    }
    routed = route_pm_l3_decision(decision)
    assert routed["routing_status"] == "phase_step_completed"

    handoff = build_browser_handoff_block(
        direction="PM_L3_TO_PM_L2",
        handoff_id="phase-3-e2e-pm-l2-handoff",
        root_task="Create FlowiseAI PM Orchestration system",
        task_id="phase-3-e2e",
        current_goal="Return final PM L2 evidence package",
        exact_task_for_receiver="Review repository-local Phase 3 closure evidence",
        created_at=CREATED_AT,
        verified_current_state=[{"fact": "repository-local e2e completed", "proof": "test fixture"}],
        relevant_repository_state={"repository_full_name": "Viktoryyyyy/flowiseai", "base_sha": BASE_SHA},
        approved_scope=["universal_role_runner/**", "tests/runtime/**", "docs/orchestration/**"],
        forbidden_scope=["server filesystem", "deployment", "runtime smoke"],
        acceptance_criteria=["PM L2 package generated"],
    )
    assert "HANDOFF_BLOCK" in handoff["copy_block"]
    assert handoff["handoff"]["to_role"] == "PM_L2_PHASE_OWNER"

    evidence = aggregate_evidence_package(
        package_id="phase-3-e2e-evidence",
        phase="Phase 3",
        repository_state={"repository_full_name": "Viktoryyyyy/flowiseai", "base_sha": BASE_SHA},
        pr_evidence=[{"pr_number": 0, "title": "repo-local e2e simulation", "head_sha": BASE_SHA}],
        ci_evidence=[{"workflow": "tests", "run_id": 0, "job_id": 0, "conclusion": "repo-local"}],
        changed_files=["universal_role_runner/browser_handoffs.py", "universal_role_runner/evidence_packages.py"],
        decision_trail=[routed["next_step_artifact"]],
        blockers=[],
        next_action="close Phase 3",
        created_at=CREATED_AT,
    )
    assert evidence_package_is_decision_ready(evidence) is True
    assert operations.repository.count_rows("role_outputs") == 2
