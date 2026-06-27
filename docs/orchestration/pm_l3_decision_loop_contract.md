# PM L3 Decision Loop Contract

Status: contract package only  
Project: MOEX Bot  
Lane: flowiseai_pm_orchestration

## Purpose

This document defines the PM L3 orchestration decision loop. PM L3 validates role outputs, decides the next role, routes correction tasks, raises blockers, and returns final evidence to PM L2.

## Lifecycle

1. Receive a PM L2-approved phase scope.
2. Confirm lane, execution mode, approved scope, forbidden scope, authority boundary, and acceptance criteria.
3. Create or continue a PhaseRun.
4. Create one RoleTask for the next required role.
5. Require the role to return handoff intake before material work.
6. Validate the returned RoleOutput.
7. Emit one PM L3 Decision:
   - route_next_role
   - accept_role_output
   - reject_role_output
   - request_correction
   - raise_blocker
   - complete_phase_step
   - return_to_pm_l2
8. Continue until acceptance criteria are satisfied or a blocker is raised.

## Decision inputs

A PM L3 decision must be based on the PhaseRun, latest RoleTask, latest RoleOutput, approved scope, CI/test evidence when required, and authority boundary.

## Acceptance decision

PM L3 may accept a role output only when it is aligned with the root task, inside approved scope, supported by evidence, and compatible with authority boundaries.

## Rejection and correction

A rejection must identify exact failed criteria. A correction task must stay within the existing approved scope. If correction requires new files, runtime behavior, CI configuration, deployment, server apply, or secrets, PM L3 must raise a blocker instead of widening scope.

## Blocker decision

A blocker must record blocker code, evidence, material impact, and required upstream decision. PM L3 must not continue material work while a blocker invalidates the active task.

## Routing target

The routing target must state the next role, target queue, and whether a browser handoff block is required. Browser mode requires a self-contained copy block. Automated mode requires resolved DB or repository references.

## Audit semantics

Each decision is an audit-worthy event. Future runtime phases should persist the decision as append-only evidence tied to the PhaseRun and RoleTask.

## Non-goals

This contract does not authorize PM L3 to merge PRs, write runtime code, deploy Flowise, apply server changes, or bypass PM L2.
