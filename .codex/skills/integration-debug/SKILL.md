---
name: integration-debug
description: Run and repair a repository's selected ASP.NET Core integration tier by discovering its own entrypoint and fixture contract, reproducing the narrowest failure, reading assertion and server output before the stack trace, separating environment, reset, seed, application and assertion faults, and verifying the exact test plus its owning project. Use when an integration test or integration CI job fails.
kind: operation
domain: dotnet
profile: integration-testing
applicability: ASP.NET Core integration suites with a real database reset between tests
requires: aspnet-core, xunit, testcontainers, respawn
provenance: framework, library, operation
---

# Debugging a .NET integration suite

Read and follow the [canonical shared definition](../../../.agents/operation/integration-debug/SKILL.md) in full.
This discovery entry is generated; edit the referenced `.agents/` definition.
