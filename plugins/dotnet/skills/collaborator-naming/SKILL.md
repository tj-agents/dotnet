---
name: collaborator-naming
description: Name C# collaborators by responsibility — application services, resolvers, calculators, factories, builders, generators, clients, stores, providers, accessors and evaluators. Covers role qualifiers and construction ownership. Use when designing or reviewing a collaborator, including one registered with dependency injection.
kind: contract
domain: dotnet
profile: core
applicability: all C# and .NET code
requires: none
provenance: language, house
---

# Collaborator naming

## Applicability

These conventions apply to C# collaborators with or without a DI container. Shared identifiers follow
[dotnet:csharp-naming](../csharp-naming/SKILL.md). Registration and lifetime mechanics belong to
[dotnet:dependency-injection](../dependency-injection/SKILL.md) when that library is selected.

## Name the responsibility and its operation

Choose the subject and role from the implementation's contract and its production callers. A role
suffix describes work the type actually owns. Registration, operation count and asynchronous execution
are independent of that responsibility.

| Responsibility | Type and operation convention |
|---|---|
| Orchestrate an application use case | `OrderService.PlaceAsync` |
| Select or resolve using rules and inputs | `DeliveryOptionResolver.ResolveAsync` |
| Compute a value | `TaxCalculator.Calculate` |
| Construct instances/components | `ConnectionFactory.Create` |
| Produce a value or artifact in one operation | `ReferenceGenerator.Generate` |
| Accumulate mutable construction steps | `DocumentBuilder.Build` |
| Call an external API | `ShippingClient.GetTrackingAsync` |
| Read and write opaque bytes or blobs | `DocumentStore.ReadAsync` / `WriteAsync` |
| Supply a value or pluggable strategy | `TimeProvider.GetUtcNow` |
| Expose a current or ambient value | `RequestContextAccessor.Current` |
| React to an event or message | `OrderPlacedHandler.HandleAsync` |
| Render, serialize or export | `InvoiceRenderer.Render`, `OrderSerializer.Serialize`, `ReportExporter.Export` |
| Decide over peer inputs | `TransitionEvaluator.Evaluate(current, observed)` |

Entity persistence follows the repository capabilities in
[dotnet:persistence](../persistence/SKILL.md). Type conversion follows
[dotnet:mapping](../mapping/SKILL.md). A one-operation repository retains its repository role, just as a
one-operation application service retains its service role.

`Resolver.Resolve` owns selection and resolution rules, including asynchronous resolution. It obtains
persisted inputs through repository query contracts, applies those rules and produces the resolved result.
The repositories retain querying, projection, persistence and locking; the resolver owns interpreting and
combining their results. A simple keyed retrieval belongs to the repository's finder contract.

Review the implementation and dependencies before changing a role name. Extract mixed responsibilities
into their owners, then update contracts, registrations and callers together. Preserving a useful verb
means keeping it on the component that owns that operation.

## Place construction with its owner

Use a named static creation method for construction owned by the domain type itself. Use a factory or
generator when production callers consume a separate construction responsibility, a family of outputs,
or construction owned by an outer layer. Seed construction follows [dotnet:seeding](../seeding/SKILL.md)
when that profile is selected.

## Qualifiers describe real distinctions

A role qualifier distinguishes alternatives the caller actually has, such as a primary and fallback
resolver. A capability or shape qualifier states a guarantee of its own: `Read` describes mutability,
and `Snapshot` describes captured state. Name the default role plainly and add the distinctions callers
need. Framework-owned interfaces retain their framework names.

`Helper` and `Utility` describe static collections of pure functions in this house convention. Prefer
the subject and operation for a cohesive function family; injected collaborators use their owned role.
