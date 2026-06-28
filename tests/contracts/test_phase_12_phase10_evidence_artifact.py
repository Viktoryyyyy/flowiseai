from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

PHASE10_EVIDENCE = REPO_ROOT / "docs" / "evidence" / "phase_10_hardening_controlled_run_001.md"
PHASE12_TASK = REPO_ROOT / "docs" / "orchestration" / "phase_12_live_github_execution_task.md"
CANONICAL_PHASE10 = REPO_ROOT / "docs" / "orchestration" / "evidence" / "phase_10_controlled_run_2026-06-28.md"


def read_text(path: Path) -> str:
    assert path.exists(), f"missing required artifact: {path}"
    return path.read_text(encoding="utf-8")


def test_phase10_hardening_evidence_artifact_preserves_required_identity():
    text = read_text(PHASE10_EVIDENCE)

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


def test_phase12_task_records_flowise_blocker_and_direct_github_fallback():
    text = read_text(PHASE12_TASK)

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


def test_canonical_phase10_artifact_remains_present_and_accepted():
    text = read_text(CANONICAL_PHASE10)

    assert "# Phase 10 Controlled Run Evidence Package" in text
    assert "final_status: \"accepted_by_PM_L2\"" in text
    assert "execution_id: \"04c5238e-ab3a-4390-bd89-9cd137ced7e8\"" in text
    assert "graph_flowData_sha256: \"6b217ffe57774473f841baef4a470d93227f5cf48814ec46b45d5323cd9282ff\"" in text


def test_phase12_documents_approved_file_scope_exactly():
    text = read_text(PHASE12_TASK)

    approved_scope = [
        "docs/evidence/phase_10_hardening_controlled_run_001.md",
        "docs/orchestration/phase_12_live_github_execution_task.md",
        "tests/contracts/test_phase_12_phase10_evidence_artifact.py",
    ]

    for path in approved_scope:
        assert path in text

    assert "approved_file_scope" in text
