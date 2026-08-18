---
name: persistence
description: EF Core persistence standard for a .NET service — the per-module `Repository<T>` base that binds the shared bases to that module's `DbContext` and key type, concrete repositories that add only the finders the base cannot express, never re-declaring inherited CRUD, the `context` field name, repositories that never leak `IQueryable`, schema and table names as module constants rather than scattered string literals, `CancellationToken` on every async method that can reach I/O, projecting a page with `IPagination<T>.Map` instead of reconstructing it, and choosing between a single `SaveChanges`, an explicit transaction, and an ambient cross-module scope. Use when adding a repository or a query, configuring an entity, mapping a paged result, or deciding how a write is committed.
---

# persistence

The standard is `../../standards/dotnet/data/PERSISTENCE.md` in `tomjseery/dotagents`, deployed to `~/.agents/standards/dotnet/data/PERSISTENCE.md`. Read it and follow it; this skill only routes to it.
