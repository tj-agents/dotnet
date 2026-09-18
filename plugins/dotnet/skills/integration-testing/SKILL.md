---
name: integration-testing
description: Integration-test standard for .NET services — each service owns a fixture project that boots its real `Program` through `WebApplicationFactory` against a containerized database reset between tests, every service-agnostic setup step lifted into a shared testing library instead of copy-pasted per fixture, header-based test authentication, dispatching integration events straight to their handlers in one scope through an `IScoped<T>` abstraction rather than hand-rolled `CreateScope`, environment names as extension members rather than raw literals, one `<Resource><Qualifier>ApiTests` class per public resource with a `#region` per operation and a real reason required before splitting, each endpoint test proving its own observable contract rather than a routes-all-return-OK sweep, module tests staying at their owning public boundary while cross-module journeys go to the process integration tier, and deterministic-failure and locking helpers staying fixture infrastructure rather than production DbContext members. Use when adding an integration test or fixture, wiring shared test setup, resolving scoped services or handlers in a test, or deciding whether a test earns a new class.

kind: contract
---

# integration-testing

The standard is `../../standards/dotnet/testing/INTEGRATION.md`, shipped in this plugin. Read it and follow it; this skill only routes to it.
