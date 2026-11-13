---
name: debug-integration
description: Use when an ASP.NET integration test fails; isolate startup, fixture/reset, seed, application and assertion causes in its own harness.
kind: operation
domain: dotnet
profile: integration-testing
applicability: ASP.NET Core integration suites with a real database reset between tests
requires: aspnet-core, xunit, testcontainers, respawn
provenance: framework, library, operation
---

# Debugging a .NET integration suite

Read and follow the [canonical definition](../../../.agents/dotnet/operation/debug/integration/SKILL.md) in full.
This discovery entry is generated; edit the referenced `.agents/` definition.
