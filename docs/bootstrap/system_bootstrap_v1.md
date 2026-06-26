# System Bootstrap v1

## Baseline

Repository: `Viktoryyyyy/flowiseai`  
Default branch: `main`  
Empty-main baseline SHA: `255b537488084b3dbc10f777babda98a70ad979a`  
Baseline evidence: commit title `Delete remaining schema file`, removing `contracts/schemas/role-output.schema.json`.

This baseline is the clean-canvas reset point for bootstrap v1.

## Objectives

Bootstrap v1 creates the initial repository-wide orchestration foundation:

1. PM orchestration documentation.
2. Repository principles.
3. JSON Schema Draft 2020-12 contracts for tasks, handoffs, role outputs, and audit events.
4. Execution mapping between roles, lanes, execution modes, output types, and validators.
5. Flowise skeleton descriptors.
6. State API contract stub.
7. Credentials policy.
8. GitHub Actions contract validation.
9. Contract tests for required files, schemas, YAML, no-secret checks, and no-runtime-claim checks.

## Non-objectives

Bootstrap v1 does not include:

- Flowise runtime deployment;
- State API implementation;
- production runtime topology;
- runtime smoke;
- server apply;
- live endpoints;
- secrets or credentials;
- MOEX trading strategy implementation.

## Approved 20-file scope

1. `README.md`
2. `docs/bootstrap/system_bootstrap_v1.md`
3. `docs/architecture-overview.md`
4. `docs/pm_l2_flow_tz.yaml`
5. `00_CORE_CONSTITUTION/repository-principles.md`
6. `contracts/schemas/task.schema.json`
7. `contracts/schemas/role-output.schema.json`
8. `contracts/schemas/handoff.schema.json`
9. `contracts/schemas/audit-event.schema.json`
10. `contracts/bindings/execution_mapping.yaml`
11. `flowise/orchestrator/root_flow.json`
12. `flowise/orchestrator/router.json`
13. `flowise/subchat/subchat_contract.json`
14. `state_api/runtime_stub/state_api_contract.yaml`
15. `security/credentials-policy.md`
16. `.github/workflows/tests.yml`
17. `ci/README.md`
18. `tests/contract/test_json_schemas.py`
19. `tests/contract/test_yaml_contracts.py`
20. `tests/contract/test_required_bootstrap_files.py`

No listed file is deferred. No other path is part of bootstrap v1 implementation scope.

## Gates

### Design gate

The design gate defines the contract decisions, required file set, authority boundaries, and validation rules.

### Implementation gate

The implementation gate creates exactly the approved 20 files on branch `integration/flowiseai-bootstrap-v1` and opens one PR to `main`.

### Validation gate

The validation gate checks syntax, JSON Schema validity, YAML parsing, required file presence, Flowise skeleton flags, State API stub flags, no-secret controls, and no positive runtime claim.

### PM L2 review gate

PM L2 reviews the PR, changed-file scope, and CI evidence. CI pass is evidence only and is not merge approval.

## Runtime boundary

No runtime smoke and no server apply are authorized in this phase. Any future runtime phase must be separately scoped and approved.
