---
name: query-building
description: Injected EF Core QueryBuilder services that resolve concrete inputs, compose specifications and return deferred IQueryable queries for a repository to execute, with explicit dependency lifetimes and no retained operation state. Use when adding, naming, registering or reviewing a DI query builder or separating query composition from specification criteria and materialization.
kind: contract
domain: dotnet
profile: ef-core
applicability: EF Core projects extracting query composition into injected collaborators
requires: ef-core
provenance: library, house
---

# EF Core query building

Read and follow the [canonical definition](../../../.agents/efcore/contract/query-building/SKILL.md) in full.
This discovery entry is generated; edit the referenced `.agents/` definition.
