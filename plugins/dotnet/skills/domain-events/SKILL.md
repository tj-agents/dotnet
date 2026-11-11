---
name: domain-events
description: Use when raising .NET domain events, defining handlers or translating them to integration events through the owning commit boundary.
kind: contract
domain: dotnet
profile: domain-model
applicability: domain models raising and dispatching in-process events
requires: domain-events
provenance: library, architecture, house
---

# Domain events — raised in the domain, dispatched by the save, published as integration events

Read and follow the [canonical definition](../../.agents/dotnet/contract/domain/events/SKILL.md) in full.
This discovery entry is generated; edit the referenced `.agents/` definition.
