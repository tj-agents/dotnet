---
name: multitenancy
description: Multi-tenant EF Core standard — visibility comes from what a context is composed from, never from disabling a filter per query (`IgnoreQueryFilters` banned via `RS0030`), the anemic per-module configuration provider that every stance composes, the tenant-scoped / read-only / admin-writable context stances, one data-access stance per query class, declaring a filter per entity rather than deriving it from a marker interface, filtering only where an entity's *reads* are tenant-private, and the independent naming dimensions (stance, mutability, projection shape) for repository qualifiers. Use when adding a `DbContext` or a repository to a tenant-aware module, deciding whether an entity should be query-filtered, hitting data that a filter is hiding, or reviewing any code that wants to bypass a global query filter.
---

# multitenancy

The standard is `standards/dotnet/data/MULTITENANCY.md` in `tomjseery/dotagents`, deployed to `~/.agents/standards/dotnet/data/MULTITENANCY.md`. Read it and follow it; this skill only routes to it.
