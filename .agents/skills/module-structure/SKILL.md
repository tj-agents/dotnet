---
name: module-structure
description: How a module or shared library inside a .NET service is laid out — the Contracts/Domain/Application/Infrastructure/Api layer split with its inward-only reference graph, which layers a given component actually needs, the visibility cascade (public contracts, internal domain/application/infrastructure, `InternalsVisibleTo` for siblings and tests), project and folder naming, and the cross-module rules — no cross-module queries even from a read stance, communication only through a module facade or an integration event, primitive foreign keys across boundaries, shared reference vocabulary as an enum rather than a table, and facades that adapt an application use case instead of reimplementing one. Use when creating a project, deciding which layer a type belongs in, promoting a type to public, or wiring one module to another.
---

# module-structure

The standard is `standards/dotnet/structure/MODULES.md` in `tomjseery/dotagents`, deployed to `~/.agents/standards/dotagents/dotnet/structure/MODULES.md`. Read it and follow it; this skill only routes to it.
