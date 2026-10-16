---
name: testing-unit
description: Unit-test standard for .NET — integration is the default for application services, handlers, controllers, repositories, DI, adapters and collaborator orchestration; unit tests are reserved for substantial deterministic core logic such as calculations, validators, decision tables, value objects and domain transitions, never mock-interaction coverage of guard clauses or delegation. Also owns xUnit shape, constructor-built SUTs, real collaborators and self-verifying architecture allowlists; test naming and the assertion library are owned by `dotnet:testing`. Use when adding or reviewing a test or deciding between the unit and integration tiers.
kind: contract
domain: dotnet
profile: unit-testing
applicability: projects using xUnit for deterministic core logic
requires: xunit
provenance: library, house
---

# Unit tests

Read and follow the [canonical definition](../../.agents/dotnet/contract/testing/unit/SKILL.md) in full.
This discovery entry is generated; edit the referenced `.agents/` definition.
