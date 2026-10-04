---
name: multitenancy
description: Multi-tenant EF Core standard — visibility comes from what a context is composed from, never from disabling a filter per query (`IgnoreQueryFilters` banned via `RS0030`), the anemic per-module configuration provider that every stance composes, the tenant-scoped / read-only / privileged-writable context stances and the verbatim shape of each (bases own `OnModelCreating`; a read context exposes named `IQueryable`s through an explicitly-implemented `IXReadDbContext` that never extends `IReadDbContext` and must have a production consumer), the uniform DI registration of a stance, the per-module stance test, one data-access stance per query class, declaring a filter per entity rather than deriving it from a marker interface, filtering only where an entity's *reads* are tenant-private, and the independent naming dimensions (stance — `Private` tenant-scoped versus `Privileged` unfiltered — mutability, projection shape) for repository qualifiers. Use when adding a `DbContext` or a repository to a tenant-aware module, wiring a context into DI, deciding whether an entity should be query-filtered, hitting data that a filter is hiding, or reviewing any code that wants to bypass a global query filter.
kind: contract
domain: dotnet
profile: multitenancy
applicability: multi-tenant projects using EF Core
requires: ef-core, multitenancy
provenance: library, architecture, house
---

# Multitenancy

Read and follow the [canonical definition](../../../.agents/dotnet/contract/multitenancy/SKILL.md) in full.
This discovery entry is generated; edit the referenced `.agents/` definition.
