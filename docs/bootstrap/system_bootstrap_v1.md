# MOEX BOT — SYSTEM BOOTSTRAP v1

## Architecture Core

- FlowiseAI = orchestration layer
- State API = source of truth
- GitHub = system of record

## Execution Model

Request → Flowise Root → PM L3 → Sub-chat → State API → Audit Event

## Roles

- PM L1: control tower
- PM L2: phase owner
- PM L3: decomposition + routing
- Sub-chat: execution unit

## State Model

All state is event-sourced and append-only.

No runtime entity may override State API.

## Contract System

All execution entities are defined in contracts/ layer.