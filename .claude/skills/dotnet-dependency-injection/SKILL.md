---
name: dependency-injection
description: Dependency-injection standard for .NET services — interface-typed dependencies and interface-to-implementation registrations in the owning composition root, constructor injection rather than `IServiceProvider` or factory lambdas, third-party SDKs registered through the vendor's own extension and kept behind an infrastructure adapter, and the dependency-holder shape (public get-only auto-properties assigned from concrete constructor parameters) for a type whose whole job is surfacing its dependencies. Use when registering a service, wiring a composition root, injecting a new dependency, integrating a third-party SDK, or reviewing a type that resolves services at runtime.
kind: contract
domain: dotnet
profile: extensions
applicability: projects using Microsoft.Extensions.DependencyInjection
requires: microsoft-extensions-dependency-injection
provenance: library, house
---

# Dependency injection

Read and follow the [canonical definition](../../../.agents/dotnet/contract/dependency-injection/SKILL.md) in full.
This discovery entry is generated; edit the referenced `.agents/` definition.
