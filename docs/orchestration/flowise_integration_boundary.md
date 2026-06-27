# Flowise Integration Boundary

Status: contract package only  
Project: MOEX Bot  
Lane: flowiseai_pm_orchestration

## Purpose

This document defines the boundary between repository contracts and future Flowise integration. Phase 2D does not implement Flowise runtime.

## Contract-only integration model

The repository describes what future Flowise or automation nodes must exchange:

- PhaseRun state
- RoleTask input context
- TaskClaimLease state
- RoleOutput structured payload
- PM L3 Decision routing payload
- GitHubExecutionRequest and result evidence
- audit events

## Future Flowise responsibilities

A future Flowise implementation may claim tasks, resolve context, assemble prompts, call model roles, validate outputs, persist immutable evidence, and route next decisions. That work requires a future explicit runtime phase.

## Boundary rules

Flowise nodes must not infer authority. They must consume the authority boundary from the task contract and fail closed if any required field is absent.

Flowise nodes must not add secrets, private endpoints, server paths, deployment commands, runtime smoke steps, or direct main writes unless a later approved phase explicitly changes the boundary.

## Prompt assembly

Prompt assembly belongs at the integration boundary. It may combine static context, role context, and dynamic task context, but it must preserve the approved scope exactly.

## Persistence

Future integration must persist outputs as immutable records. Browser chat text is not durable runtime state.

## Non-goals

This document does not define Flowise credentials, node configuration, deployment topology, server installation, database schema migration, or runtime smoke procedure.
