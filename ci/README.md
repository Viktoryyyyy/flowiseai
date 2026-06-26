# CI Validation Scope

The `tests` workflow validates bootstrap-v1 contracts only.

## Validation included

CI checks:

- JSON Schema Draft 2020-12 syntax and metaschema validity;
- representative sample instances for task, handoff, role output, and audit event;
- YAML parsing and required top-level keys;
- required bootstrap file presence and non-empty content;
- Flowise skeleton flags;
- State API contract stub flags;
- no likely secret values;
- no live runtime endpoint values;
- no positive runtime claim.

## Validation excluded

CI does not deploy Flowise. CI does not implement or call the State API. CI does not perform server apply. CI does not perform runtime smoke.

A CI pass is evidence for PM review. It is not PM L2 merge approval and does not prove production readiness.
