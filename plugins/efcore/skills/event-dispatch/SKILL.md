---
name: event-dispatch
description: EF Core domain-event dispatch through SaveChanges interceptors, clearing collected events, transactional pre-commit work and the distinction between saving and committing an enclosing transaction. Use when implementing or reviewing event dispatch around EF Core SaveChanges, an outbox, or an explicit transaction.
kind: contract
domain: dotnet
profile: domain-model
applicability: EF Core projects dispatching domain events at the persistence boundary
requires: ef-core, domain-events
provenance: library, architecture, house
---

# EF Core event dispatch

Read and follow the [canonical definition](../../.agents/efcore/contract/event-dispatch/SKILL.md) in full.
This discovery entry is generated; edit the referenced `.agents/` definition.
