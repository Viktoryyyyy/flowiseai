from __future__ import annotations

import json
import pathlib
from typing import Any

import pytest
import yaml
from jsonschema import Draft202012Validator, ValidationError

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

REQUEST_SCHEMA_PATH = REPO_ROOT / 'contracts' / 'flowise' / 'flowise_run_request.schema.json'
RESULT_SCHEMA_PATH = REPO_ROOT / 'contracts' / 'flowise' / 'flowise_run_result.schema.json'
PM_L3_SCHEMA_PATH = REPO_ROOT / 'contracts' / 'pm' / 'pm_l3_task_envelope.schema.json'
STATUS_TAXONOMY_PATH = REPO_ROOT / 'contracts' / 'taxonomy' / 'status_taxonomy.yaml'
BLOCKER_TAXONOMY_PATH = REPO_ROOT / 'contracts' / 'taxonomy' / 'blocker_taxonomy.yaml'

APPROVED_SCOPE = [
    'contracts/flowise/flowise_run_request.schema.json',
    'contracts/flowise/flowise_run_result.schema.json',
    'contracts/pm/pm_l3_task_envelope.schema.json',
    'contracts/taxonomy/status_taxonomy.yaml',
    'contracts/taxonomy/blocker_taxonomy.yaml',
    'contracts/correlation/correlation_model.md',
    'docs/orchestration/phase_8_contract_artifacts.md',
    'tests/contracts/test_phase_8_flowise_contracts.py',
]

FORBIDDEN_ACTIONS = [
    'server_changes',
    'deployment',
    'flowise_runtime_modification',
    'production_graph_changes',
    'secrets',
    'direct_main_write',
    'merge_without_pm_l2_authority',
    'phase_3_4_5_6_architecture_change',
]


def load_json(path: pathlib.Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))


def load_yaml(path: pathlib.Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding='utf-8'))
    assert isinstance(data, dict), path
    return data


def envelope() -> dict[str, Any]:
    return {
        'envelope_version': '1.0.0',
        'envelope_id': 'pm-l3-task-envelope-phase-8',
        'correlation_id': 'corr-phase-8-contract-artifacts',
        'task_id': 'flowiseai-phase-8-contract-artifacts',
        'project': 'MOEX Bot + FlowiseAI',
        'phase': 'Phase 8',
        'lane': 'flowiseai_pm_orchestration',
        'execution_mode': 'browser_chatgpt_github_direct',
        'assigned_role': 'SUBCHAT_IMPLEMENTATION',
        'repository_full_name': 'Viktoryyyyy/flowiseai',
        'base_ref': 'origin/main',
        'branch_name': 'flowiseai-pm/phase-8-contract-artifacts',
        'approved_file_scope': APPROVED_SCOPE,
        'forbidden_actions': FORBIDDEN_ACTIONS,
        'authority_boundary': {
            'merge_authority': 'PM_L2_ONLY',
            'direct_main_write_allowed': False,
            'server_apply_allowed': False,
            'deployment_allowed': False,
            'runtime_allowed': False,
        },
        'contract_refs': {
            'flowise_run_request_schema': 'contracts/flowise/flowise_run_request.schema.json',
            'flowise_run_result_schema': 'contracts/flowise/flowise_run_result.schema.json',
            'status_taxonomy': 'contracts/taxonomy/status_taxonomy.yaml',
            'blocker_taxonomy': 'contracts/taxonomy/blocker_taxonomy.yaml',
            'correlation_model': 'contracts/correlation/correlation_model.md',
        },
        'acceptance_criteria': ['Phase 8 contract artifacts exist'],
        'stop_conditions': ['scope change'],
        'created_at': '2026-06-27T00:00:00Z',
        'metadata': {},
    }


def request() -> dict[str, Any]:
    return {
        'contract_version': '1.0.0',
        'request_id': 'flowise-run-request-phase-8',
        'correlation_id': 'corr-phase-8-contract-artifacts',
        'idempotency_key': 'phase-8-idempotency-key',
        'project': 'MOEX Bot + FlowiseAI',
        'phase': 'Phase 8',
        'lane': 'flowiseai_pm_orchestration',
        'execution_mode': 'browser_chatgpt_github_direct',
        'source_role': 'PM_L3_DELIVERY_VALIDATION_OWNER',
        'target_flow': {'flow_kind': 'agentflow_v2', 'flow_identifier': 'phase-8-contract-validation', 'runtime_url': 'none'},
        'task_id': 'flowiseai-phase-8-contract-artifacts',
        'pm_l3_task_envelope': envelope(),
        'input_payload': {'instructions': 'validate contract artifacts only'},
        'authority_boundary': {
            'merge_authority': 'PM_L2_ONLY',
            'direct_main_write_allowed': False,
            'server_apply_allowed': False,
            'deployment_allowed': False,
            'runtime_modification_allowed': False,
            'production_graph_change_allowed': False,
            'secrets_allowed': False,
        },
        'status': 'created',
        'blockers': [],
        'created_at': '2026-06-27T00:00:00Z',
        'metadata': {},
    }


def result(status: str = 'succeeded') -> dict[str, Any]:
    blockers: list[dict[str, str]] = []
    outcome = 'completed'
    if status == 'blocked':
        outcome = 'blocked'
        blockers = [{'blocker_code': 'scope_violation', 'severity': 'blocking', 'message': 'scope mismatch'}]
    if status == 'failed':
        outcome = 'failed'
        blockers = [{'blocker_code': 'ci_failed_implementation', 'severity': 'blocking', 'message': 'contract test failed'}]
    if status == 'cancelled':
        outcome = 'no_op'
    return {
        'contract_version': '1.0.0',
        'result_id': 'flowise-run-result-phase-8',
        'request_id': 'flowise-run-request-phase-8',
        'correlation_id': 'corr-phase-8-contract-artifacts',
        'idempotency_key': 'phase-8-idempotency-key',
        'project': 'MOEX Bot + FlowiseAI',
        'phase': 'Phase 8',
        'lane': 'flowiseai_pm_orchestration',
        'execution_mode': 'browser_chatgpt_github_direct',
        'status': status,
        'outcome': outcome,
        'output_payload': {'role_output_type': 'implementation_report', 'summary': 'validated', 'artifacts': APPROVED_SCOPE},
        'blockers': blockers,
        'authority_boundary': {
            'merge_performed': False,
            'direct_main_write_performed': False,
            'server_apply_performed': False,
            'deployment_performed': False,
            'runtime_modification_performed': False,
            'production_graph_change_performed': False,
            'secrets_exposed': False,
        },
        'started_at': '2026-06-27T00:00:00Z',
        'completed_at': '2026-06-27T00:01:00Z',
        'metadata': {},
    }


def test_phase_8_json_schemas_are_valid() -> None:
    for path in [REQUEST_SCHEMA_PATH, RESULT_SCHEMA_PATH, PM_L3_SCHEMA_PATH]:
        schema = load_json(path)
        assert schema['$schema'] == 'https://json-schema.org/draft/2020-12/schema'
        Draft202012Validator.check_schema(schema)


def test_minimal_phase_8_instances_validate() -> None:
    Draft202012Validator(load_json(PM_L3_SCHEMA_PATH)).validate(envelope())
    Draft202012Validator(load_json(REQUEST_SCHEMA_PATH)).validate(request())
    Draft202012Validator(load_json(RESULT_SCHEMA_PATH)).validate(result())


def test_required_fields_are_enforced() -> None:
    instance = request()
    instance.pop('correlation_id')
    with pytest.raises(ValidationError):
        Draft202012Validator(load_json(REQUEST_SCHEMA_PATH)).validate(instance)


def test_enum_values_are_enforced() -> None:
    instance = result()
    instance['status'] = 'partially_done'
    with pytest.raises(ValidationError):
        Draft202012Validator(load_json(RESULT_SCHEMA_PATH)).validate(instance)


@pytest.mark.parametrize('field', [
    'direct_main_write_allowed',
    'server_apply_allowed',
    'deployment_allowed',
    'runtime_modification_allowed',
    'production_graph_change_allowed',
    'secrets_allowed',
])
def test_request_authority_boundary_constraints_are_fail_closed(field: str) -> None:
    instance = request()
    instance['authority_boundary'][field] = True
    with pytest.raises(ValidationError):
        Draft202012Validator(load_json(REQUEST_SCHEMA_PATH)).validate(instance)


@pytest.mark.parametrize('field', [
    'merge_performed',
    'direct_main_write_performed',
    'server_apply_performed',
    'deployment_performed',
    'runtime_modification_performed',
    'production_graph_change_performed',
    'secrets_exposed',
])
def test_result_authority_boundary_constraints_are_fail_closed(field: str) -> None:
    instance = result()
    instance['authority_boundary'][field] = True
    with pytest.raises(ValidationError):
        Draft202012Validator(load_json(RESULT_SCHEMA_PATH)).validate(instance)


def test_correlation_field_echo_rules() -> None:
    env = envelope()
    req = request()
    res = result()
    assert req['correlation_id'] == env['correlation_id']
    assert res['correlation_id'] == req['correlation_id']
    assert res['request_id'] == req['request_id']
    assert res['idempotency_key'] == req['idempotency_key']


def test_blocker_and_status_consistency() -> None:
    schema = load_json(RESULT_SCHEMA_PATH)
    Draft202012Validator(schema).validate(result('blocked'))
    bad = result('blocked')
    bad['blockers'] = []
    with pytest.raises(ValidationError):
        Draft202012Validator(schema).validate(bad)

    statuses = load_yaml(STATUS_TAXONOMY_PATH)
    blockers = load_yaml(BLOCKER_TAXONOMY_PATH)
    assert 'blocked_status_requires_blocker' in {rule['rule_id'] for rule in statuses['consistency_rules']}
    assert result('blocked')['blockers'][0]['blocker_code'] in blockers['blocker_codes']


def test_phase_7_forbidden_actions_remain_blocked() -> None:
    Draft202012Validator(load_json(PM_L3_SCHEMA_PATH)).validate(envelope())
    blockers = load_yaml(BLOCKER_TAXONOMY_PATH)
    assert set(FORBIDDEN_ACTIONS) == set(blockers['forbidden_action_map'])
    for action, blocker_code in blockers['forbidden_action_map'].items():
        assert action in envelope()['forbidden_actions']
        assert blockers['blocker_codes'][blocker_code]['severity'] == 'blocking'
