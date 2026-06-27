# GitHub Execution Boundary Contract

Status: contract package only  
Project: MOEX Bot  
Lane: flowiseai_pm_orchestration

## Purpose

This document defines the safe boundary for GitHub execution requests produced by orchestration roles.

## Allowed operation classes

A GitHubExecutionRequest may request only an approved repository operation:

- create the approved branch from current main
- commit the approved file scope to the approved branch
- open or update one PR to main
- verify CI on the latest PR head SHA
- collect evidence for PM L3 and PM L2

## Required request fields

A request must include repository, base ref, base SHA, branch name, approved file scope, PR metadata, CI expectation, result evidence fields, and safety boundaries.

## Safety boundaries

The request must explicitly state:

- direct main write is not allowed
- server apply is not allowed
- deployment is not allowed
- runtime smoke is not allowed
- secrets are not allowed
- private endpoints are not allowed

The schema requires secrets and private endpoint arrays to be empty.

## Result evidence

Result evidence must identify commit SHA, PR number, workflow run id, conclusion, and whether evidence is tied to the latest PR head SHA. Evidence that is not tied to the latest head SHA is insufficient for merge review.

## Scope enforcement

Actual changed files must match the approved file scope or a justified strict subset. Any outside file is a scope violation and must block the request.

## CI semantics

CI success is evidence for PM review. It is not merge approval. Failed CI is implementation evidence and must be diagnosed before classifying a tool or access blocker.

## Explicit non-goals

This boundary does not authorize merge, server apply, deployment, runtime smoke, secret injection, private endpoint configuration, or direct main mutation.
