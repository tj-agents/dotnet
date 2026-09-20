---
name: module-structure
description: How a module or shared library inside a .NET service is laid out — the Contracts/Domain/Application/Infrastructure/Api layer split with its inward-only reference graph, which layers a given component actually needs, where the clock is resolved and how the current instant reaches a domain method, the visibility cascade (public contracts, internal domain/application/infrastructure, `InternalsVisibleTo` for siblings and tests), project and folder naming, and the cross-module rules — no cross-module queries even from a read stance, communication only through a module facade or an integration event, primitive foreign keys across boundaries, shared reference vocabulary as an enum rather than a table, and facades that adapt an application use case instead of reimplementing one. Use when creating a project, deciding which layer a type belongs in, promoting a type to public, wiring one module to another, or deciding where the current time is resolved.
kind: contract
domain: dotnet
profile: modular-services
applicability: modular service or layered shared-library architecture
requires: modular-service-architecture
provenance: architecture, house
---

# Module structure

Read and follow the [canonical shared definition](../../../.agents/contract/module-structure/SKILL.md) in full.
This discovery entry is generated; edit the referenced `.agents/` definition.
