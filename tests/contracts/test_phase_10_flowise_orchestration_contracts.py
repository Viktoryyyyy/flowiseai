from __future__ import annotations

from copy import deepcopy
from typing import Any

import pytest

APPROVED_FILE_SCOPE = [
    'docs/orchestration/phase_10_production_orchestration_loop_design.md',
    'docs/orchestration/phase_10_evidence_package_template.md',
    'tests/contracts/test_phase_10_flowise_orchestration_contracts.py',
]

REQUIRED_CORRELATION_FIELDS = [
    'request_id',
    'correlation_id',
    'idempotency_key',
]

REQUIRED_FORBIDDEN_SCOPE_FLAGS = [
    'runtime_action_performed',
    'server_apply_performed',
    'n8n_action_performed',
    'direct_main_write_performed',
    'merge_performed',
    'production_deployment_performed',
    'production_graph_change_performed',
    'forbidden_files_changed',
    'secrets_exposed',
]


class EvidenceValidationError(AssertionError):
    pass


def phase_10_evidence_package() -> dict[str, Any]:
    return {
        'package_id': 'phase-10-evidence-package-wp1',
        'package_version': 1,
        'project': 'MOEX Bot + FlowiseAI',
        'phase': 'Phase 10',
        'lane': 'flowiseai_pm_orchestration',
        'task_id': 'flowiseai-phase-10-wp1-repo-artifacts',
        'created_at': '2026-06-28T00:00:00Z',
        'authority_boundary': {
            'merge_authority': 'PM_L2_ONLY',
            'direct_main_write_allowed': False,
            'server_apply_authority': 'PM_L2_ONLY_OR_EXPLICIT_PM_L2_TASK',
            'runtime_allowed': False,
            'production_deployment_allowed': False,
            'secrets_allowed_in_chat': False,
        },
        'execution_identity': {
            'execution_id': 'exec-phase-10-wp1-001',
            'correlation_id': 'corr-phase-10-wp1-001',
            'idempotency_key': 'phase-10-wp1-idempotency-key',
        },
        'runtime_evidence': {
            'production_grade_phase_10_runtime_evidence': True,
            'runtime_surface': 'Flowise AgentFlow V2',
            'runtime_status': 'not_checked',
            'execution_id': 'exec-phase-10-wp1-001',
        },
        'graph_evidence': {
            'graph_id': 'agentflow-v2-phase-10-mvp-loop',
            'graph_name': 'Phase 10 MVP Orchestration Loop',
            'graph_kind': 'agentflow_v2',
            'graph_export_sha256': 'not_captured',
            'graph_snapshot_ref': 'not_captured',
        },
        'flowise_run_request_summary': {
            'request_id': 'flowise-run-request-phase-10-wp1',
            'correlation_id': 'corr-phase-10-wp1-001',
            'idempotency_key': 'phase-10-wp1-idempotency-key',
            'task_id': 'flowiseai-phase-10-wp1-repo-artifacts',
            'source_role': 'PM_L3_DELIVERY_VALIDATION_OWNER',
            'target_flow': {
                'flow_kind': 'agentflow_v2',
                'graph_id': 'agentflow-v2-phase-10-mvp-loop',
                'graph_name': 'Phase 10 MVP Orchestration Loop',
            },
        },
        'flowise_run_result_summary': {
            'result_id': 'flowise-run-result-phase-10-wp1',
            'request_id': 'flowise-run-request-phase-10-wp1',
            'correlation_id': 'corr-phase-10-wp1-001',
            'idempotency_key': 'phase-10-wp1-idempotency-key',
            'status': 'succeeded',
            'outcome': 'completed',
            'output_type': 'implementation_report',
        },
        'role_execution_summary': {
            'assigned_role': 'SUBCHAT_IMPLEMENTATION',
            'role_task_status': 'completed',
            'outputs_created': APPROVED_FILE_SCOPE,
            'changed_files': APPROVED_FILE_SCOPE,
        },
        'blockers': [],
        'forbidden_scope_flags': {flag: False for flag in REQUIRED_FORBIDDEN_SCOPE_FLAGS},
        'validation_sequence': ['pm_l3_validation', 'pm_l2_final_verdict'],
        'pm_l3_validation': {
            'verdict': 'pass',
            'validated_at': '2026-06-28T00:01:00Z',
            'validator_role': 'PM_L3_DELIVERY_VALIDATION_OWNER',
        },
        'pm_l2_final_verdict': {
            'verdict': 'not_reviewed',
            'reviewed_at': 'not_reviewed',
            'reviewer_role': 'PM_L2_PHASE_OWNER',
            'deployment_readiness_claim': 'not_claimed',
            'pm_l2_deployment_approved': False,
        },
        'rejected_claims': [],
        'no_secrets': {
            'secrets_included': False,
            'secret_sources_checked': [
                'prompts',
                'request_summary',
                'result_summary',
                'runtime_evidence',
                'graph_evidence',
            ],
        },
    }


def validate_phase_10_evidence_package(package: dict[str, Any]) -> None:
    if package.get('phase') != 'Phase 10':
        raise EvidenceValidationError('phase must be Phase 10')

    runtime_evidence = package.get('runtime_evidence')
    if not isinstance(runtime_evidence, dict):
        raise EvidenceValidationError('runtime_evidence is required')

    if runtime_evidence.get('production_grade_phase_10_runtime_evidence'):
        execution_identity = package.get('execution_identity')
        if not isinstance(execution_identity, dict) or not execution_identity.get('execution_id'):
            raise EvidenceValidationError('execution_id is required')
        if runtime_evidence.get('execution_id') != execution_identity['execution_id']:
            raise EvidenceValidationError('runtime execution_id must match execution identity')

    graph = package.get('graph_evidence')
    if not isinstance(graph, dict):
        raise EvidenceValidationError('graph_evidence is required')
    for field in ['graph_id', 'graph_name']:
        if not graph.get(field):
            raise EvidenceValidationError(f'{field} is required')

    request = package.get('flowise_run_request_summary')
    result = package.get('flowise_run_result_summary')
    if not isinstance(request, dict) or not isinstance(result, dict):
        raise EvidenceValidationError('request and result summaries are required')
    for field in REQUIRED_CORRELATION_FIELDS:
        if not request.get(field):
            raise EvidenceValidationError(f'request {field} is required')
        if not result.get(field):
            raise EvidenceValidationError(f'result {field} is required')
        if result[field] != request[field]:
            raise EvidenceValidationError(f'{field} must correlate between request and result')
    if not result.get('result_id'):
        raise EvidenceValidationError('result_id is required')

    final_verdict = package.get('pm_l2_final_verdict')
    if not isinstance(final_verdict, dict):
        raise EvidenceValidationError('pm_l2_final_verdict is required')
    claim = final_verdict.get('deployment_readiness_claim')
    if claim in {'claimed_ready', 'deployment_ready', 'ready'} and not final_verdict.get('pm_l2_deployment_approved'):
        raise EvidenceValidationError('deployment readiness claim requires PM L2 approval')

    pm_l3_validation = package.get('pm_l3_validation')
    if not isinstance(pm_l3_validation, dict) or not pm_l3_validation.get('verdict'):
        raise EvidenceValidationError('PM L3 validation verdict is required before PM L2 final verdict')
    sequence = package.get('validation_sequence')
    if sequence != ['pm_l3_validation', 'pm_l2_final_verdict']:
        raise EvidenceValidationError('PM L3 validation must precede PM L2 final verdict')

    forbidden_flags = package.get('forbidden_scope_flags')
    if not isinstance(forbidden_flags, dict):
        raise EvidenceValidationError('forbidden_scope_flags is required')
    for flag in REQUIRED_FORBIDDEN_SCOPE_FLAGS:
        if flag not in forbidden_flags:
            raise EvidenceValidationError(f'{flag} flag is required')
        if forbidden_flags[flag] is not False:
            raise EvidenceValidationError(f'{flag} must be false')

    if 'blockers' not in package:
        raise EvidenceValidationError('blockers list is required')
    if not isinstance(package['blockers'], list):
        raise EvidenceValidationError('blockers must be a list')

    no_secrets = package.get('no_secrets')
    if not isinstance(no_secrets, dict) or no_secrets.get('secrets_included') is not False:
        raise EvidenceValidationError('evidence package must include no secrets confirmation')


def test_valid_phase_10_evidence_package_passes_contract() -> None:
    validate_phase_10_evidence_package(phase_10_evidence_package())


def test_production_grade_phase_10_runtime_evidence_requires_execution_id() -> None:
    package = phase_10_evidence_package()
    package['execution_identity'].pop('execution_id')

    with pytest.raises(EvidenceValidationError, match='execution_id'):
        validate_phase_10_evidence_package(package)


@pytest.mark.parametrize('field', ['graph_id', 'graph_name'])
def test_evidence_package_requires_graph_id_and_graph_name(field: str) -> None:
    package = phase_10_evidence_package()
    package['graph_evidence'].pop(field)

    with pytest.raises(EvidenceValidationError, match=field):
        validate_phase_10_evidence_package(package)


@pytest.mark.parametrize('field', REQUIRED_CORRELATION_FIELDS)
def test_evidence_package_requires_request_result_correlation_fields(field: str) -> None:
    package = phase_10_evidence_package()
    package['flowise_run_result_summary'][field] = f'mismatched-{field}'

    with pytest.raises(EvidenceValidationError, match=field):
        validate_phase_10_evidence_package(package)


def test_evidence_package_requires_result_id() -> None:
    package = phase_10_evidence_package()
    package['flowise_run_result_summary'].pop('result_id')

    with pytest.raises(EvidenceValidationError, match='result_id'):
        validate_phase_10_evidence_package(package)


def test_deployment_readiness_claim_is_rejected_unless_pm_l2_approved() -> None:
    package = phase_10_evidence_package()
    package['pm_l2_final_verdict']['deployment_readiness_claim'] = 'claimed_ready'
    package['pm_l2_final_verdict']['pm_l2_deployment_approved'] = False

    with pytest.raises(EvidenceValidationError, match='PM L2 approval'):
        validate_phase_10_evidence_package(package)

    package['pm_l2_final_verdict']['pm_l2_deployment_approved'] = True
    validate_phase_10_evidence_package(package)


def test_pm_l3_validation_verdict_is_required_before_pm_l2_final_verdict() -> None:
    package = phase_10_evidence_package()
    package['validation_sequence'] = ['pm_l2_final_verdict', 'pm_l3_validation']

    with pytest.raises(EvidenceValidationError, match='PM L3 validation must precede'):
        validate_phase_10_evidence_package(package)

    package = phase_10_evidence_package()
    package['pm_l3_validation'].pop('verdict')

    with pytest.raises(EvidenceValidationError, match='PM L3 validation verdict'):
        validate_phase_10_evidence_package(package)


@pytest.mark.parametrize('flag', REQUIRED_FORBIDDEN_SCOPE_FLAGS)
def test_evidence_package_records_forbidden_scope_flags(flag: str) -> None:
    package = phase_10_evidence_package()
    package['forbidden_scope_flags'].pop(flag)

    with pytest.raises(EvidenceValidationError, match=flag):
        validate_phase_10_evidence_package(package)

    package = phase_10_evidence_package()
    package['forbidden_scope_flags'][flag] = True

    with pytest.raises(EvidenceValidationError, match=flag):
        validate_phase_10_evidence_package(package)


def test_evidence_package_includes_blockers_list_even_when_empty() -> None:
    package = phase_10_evidence_package()
    package.pop('blockers')

    with pytest.raises(EvidenceValidationError, match='blockers'):
        validate_phase_10_evidence_package(package)

    package = phase_10_evidence_package()
    package['blockers'] = 'none'

    with pytest.raises(EvidenceValidationError, match='blockers'):
        validate_phase_10_evidence_package(package)

    package = phase_10_evidence_package()
    package['blockers'] = []
    validate_phase_10_evidence_package(package)
