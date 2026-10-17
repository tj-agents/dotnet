---
name: persistence
description: EF Core persistence standard for a .NET service — repositories never leak `IQueryable`, `CancellationToken` on every async method that can reach I/O, schema and table names as constants rather than scattered string literals, awaiting a mapper's prefetch before projecting rather than per-row round trips, choosing between one `SaveChanges`, an explicit transaction and an ambient cross-context scope, never sharing a transaction across services, exactly one context migrating a table with every borrower mapping it through `ExcludeFromMigrations`, and no foreign key from a write model to a read model. Use when adding a repository or a query, configuring an entity, mapping a query result, or deciding how a write is committed.
kind: contract
domain: dotnet
profile: ef-core
applicability: projects using EF Core
requires: ef-core
provenance: library
---

# Persistence

Read and follow the [canonical definition](../../../.agents/dotnet/contract/persistence/SKILL.md) in full.
This discovery entry is generated; edit the referenced `.agents/` definition.
