---
name: integration-testing
description: Integration-test standard for .NET services — each service owns a fixture project that boots its real `Program` through `WebApplicationFactory` against a containerized database reset between tests, every service-agnostic setup step lifted into a shared testing library instead of copy-pasted per fixture, header-based test authentication, dispatching integration events straight to their handlers in one scope through an `IScoped<T>` abstraction rather than hand-rolled `CreateScope`, environment names as extension members rather than raw literals, `<Resource><Qualifier>ApiTests` naming, a region per endpoint, and splitting a file when a controller varies on two axes. Use when adding an integration test or fixture, wiring shared test setup, resolving scoped services or handlers in a test, or organizing a test class that has outgrown one axis.
---

# integration-testing

The standard is `../../standards/dotnet/testing/INTEGRATION.md` in `tomjseery/dotagents`, deployed to `~/.agents/standards/dotnet/testing/INTEGRATION.md`. Read it and follow it; this skill only routes to it.
