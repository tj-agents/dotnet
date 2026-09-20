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

## Applicability

This operation applies only when the repository provides an ASP.NET Core integration tier with its own
supported entrypoint, real test database, and reset mechanism. Discover those commands and fixture names
from the consuming repository; this capability does not supply a product harness or roster.

## Procedure

1. Read the repository's test instructions and list the supported integration scopes. Never guess a project path.
2. Check only the prerequisites declared by that harness, such as Docker for Testcontainers.
3. Reproduce the narrowest failing test or project and retain its complete assertion, server output, and stack trace.
4. Read failures in that order: assertion or exception, server-side output for the request, then the stack trace.
5. Distinguish environment startup, fixture/reset ordering, seed state, application behavior, and assertion failures.
6. Fix the cause. Do not skip a test, weaken an assertion, or replace a real dependency with an in-memory substitute.
7. Re-run the exact failure, then its owning integration project. Broader CI remains the remote checkpoint.

Use `engineering:failing-tests` for general failure policy, `engineering:failure-provenance` when the failure
may predate the change, and `dotnet:integration-testing` for fixture and authoring rules.
