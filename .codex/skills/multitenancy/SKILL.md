---
name: multitenancy
description: Multi-tenant EF Core standard — visibility comes from what a context is composed from, never from disabling a filter per query (`IgnoreQueryFilters` banned via `RS0030`), one data-access stance per query class, declaring a filter per entity rather than deriving it from a marker interface, and filtering only where an entity's *reads* are tenant-private. Use when adding a `DbContext` or a repository to a tenant-aware module, deciding whether an entity should be query-filtered, hitting data that a filter is hiding, or reviewing any code that wants to bypass a global query filter.
kind: contract
domain: dotnet
profile: multitenancy
applicability: multi-tenant projects using EF Core
requires: ef-core, multitenancy
provenance: library, architecture
---

# Multitenancy

Read and follow the [canonical definition](../../../.agents/dotnet/contract/multitenancy/SKILL.md) in full.
This discovery entry is generated; edit the referenced `.agents/` definition.
