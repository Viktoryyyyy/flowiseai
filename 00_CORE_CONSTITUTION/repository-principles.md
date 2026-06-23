# Repository Principles

## Core Rules

1. GitHub is the single source of truth
2. All changes must be traceable via commits
3. No runtime system can override repository state
4. Flowise is a runtime execution engine only
5. Orchestration layer governs tasks, roles, and evidence
6. Secrets are never stored in repository
7. Credentials are reference-based only
8. All changes must follow PR-based workflow (future enforcement)

## Governance Model

- One branch = one task
- One PR = one lane
- No mixed-domain modifications
- Strict separation of flowise / orchestration / runtime

## Authority Model

- PM L2 is the only merge authority
- PM L3 validates and aggregates execution
- Sub-chats execute isolated tasks

## Sync Principle

- GitHub → Flowise is authoritative
- Flowise → GitHub is snapshot-only
