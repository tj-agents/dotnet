---
name: testing-integration
description: Use when authoring ASP.NET integration tests with the selected database harness, reset lifecycle, authentication or scoped services.
kind: contract
domain: dotnet
profile: integration-testing
applicability: ASP.NET Core integration suites with a real database reset between tests
requires: aspnet-core, xunit, testcontainers, respawn
provenance: framework, library, house
---

# Integration tests

Read and follow the [canonical definition](../../.agents/dotnet/contract/testing/integration/SKILL.md) in full.
This discovery entry is generated; edit the referenced `.agents/` definition.
