---
name: unit-testing
description: Unit-test standard for .NET — integration is the default for application services, handlers, controllers, repositories, DI, adapters and collaborator orchestration; unit tests are reserved for substantial deterministic core logic such as calculations, validators, decision tables, value objects and domain transitions, never mock-interaction coverage of guard clauses or delegation. Also owns xUnit shape and naming, constructor-built SUTs, real collaborators, assertion-library consistency and self-verifying architecture allowlists. Use when adding or reviewing a test or deciding between the unit and integration tiers.
kind: contract
domain: dotnet
profile: unit-testing
applicability: projects using xUnit for deterministic core logic
requires: xunit
provenance: library, house
---

# Unit tests

Read and follow the [canonical shared definition](../../../.agents/contract/unit-testing/SKILL.md) in full.
This discovery entry is generated; edit the referenced `.agents/` definition.
