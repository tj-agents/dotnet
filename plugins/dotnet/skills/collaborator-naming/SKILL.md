---
name: collaborator-naming
description: Canonical C# collaborator roles and operation contracts — select the subject, responsibility, verb, returned value and caller-visible outcomes together. Distinguishes resolvers, validators, services, repositories, mappers, factories, calculators, providers and accessors, with separate owners for persistence, result carriers, validation and DI. Use when designing, naming or reviewing a collaborator and its interface.
kind: contract
domain: dotnet
profile: core
applicability: all C# and .NET code
requires: none
provenance: language, house
---

# Collaborator naming and contracts

## Applicability and ownership

These are canonical house roles for C# projects, usable with or without DI. Framework and library
interfaces retain their defined contracts. Shared identifiers follow
[dotnet:csharp-naming](../csharp-naming/SKILL.md); DI registration and lifetime follow
[dotnet:dependency-injection](../dependency-injection/SKILL.md) when selected.

This owner defines what a collaborator does and how that operation is named. Payload meaning belongs
to [dotnet:data-contract-naming](../data-contract-naming/SKILL.md). Concrete success, absence and failure
carriers belong to the project's selected result contract; projects selecting Reunion use
[dotnet:result-carriers](../result-carriers/SKILL.md). The role and outcome decisions apply together.

## Select a complete operation contract

Read the implementation and production callers. Establish these five parts before naming the type:

1. Subject: the established domain concept the caller works with.
2. Responsibility: the work this component owns and the work supplied by its dependencies.
3. Operation: the action and, when useful, the particular returned shape.
4. Success value: the thing produced, selected, transformed or assessed.
5. Alternate outcomes: the distinctions the caller must handle, including absence and rejection.

A method inside an implementation contributes evidence; the component's public responsibility determines
its role. Reading data can support resolution or validation. Checking a candidate can support resolution.
Creating an object can be one step in a calculation. Name the complete responsibility the caller consumes.

## Canonical roles

| Responsibility | Type and operation | Contract observed by the caller |
|---|---|---|
| Orchestrate an application use case | `OrderService.PlaceAsync` | Operation value or completion, with the use case's expected failures |
| Select or derive a usable value from inputs, candidates or current state | `OrderResolver.ResolveSnapshotAsync` | The resolved `OrderSnapshot`, with absence or rejection when the contract permits them |
| Assess a supplied candidate against rules | `OrderValidator.ValidateCheckoutAsync` | Validation decision and diagnostics; the supplied candidate remains the candidate |
| Compute a value | `TaxCalculator.Calculate` | The computed amount; any expected failure belongs to the calculation contract |
| Construct an instance or component | `ConnectionFactory.Create` | The constructed instance |
| Accumulate construction steps | `DocumentBuilder.Build` | The completed object produced from the accumulated state |
| Generate a value or artifact | `ReferenceGenerator.Generate` | The generated reference or artifact |
| Call an external API | `ShippingClient.GetTrackingAsync` | The external capability, with outcomes translated at the client boundary |
| Read or write opaque bytes or blobs | `DocumentStore.ReadAsync` / `WriteAsync` | Stored content or write completion |
| Supply a value or pluggable strategy | `TimeProvider.GetUtcNow` | The supplied value under the provider's stated guarantee |
| Expose a current or ambient value | `RequestContextAccessor.Current` | The value already associated with that context |
| React to an event or message | `OrderPlacedHandler.HandleAsync` | Handling completion under the messaging contract |
| Render, serialize or export | `InvoiceRenderer.Render`, `OrderSerializer.Serialize`, `ReportExporter.Export` | The rendered or encoded representation |
| Decide over peer inputs | `TransitionEvaluator.Evaluate` | The decision over those inputs |

Persistence roles and their method/return contracts are owned by
[dotnet:persistence](../persistence/SKILL.md). Pure conversions are owned by
[dotnet:mapping](../mapping/SKILL.md). An operation count or DI registration does not alter these roles.

## Resolver contracts

A resolver produces a usable value. It may obtain candidates from repositories, check whether their
state satisfies the resolution inputs and combine the selected data. Repository dependencies own SQL,
projection, transaction enlistment and locks; the resolver owns interpreting their results.

Use `Resolve` plus the returned shape when that makes the contract clearer: `ResolveSnapshotAsync`,
`ResolveDetailsAsync`, or `ResolveSummaryAsync`. Use `ResolveAsync` when the subject and single output
are already unambiguous. A bulk operation names its actual domain collection or uses `ResolveManyAsync`
when it is the many-item form of the same capability. Its output defines whether unresolved items are
omitted, represented individually or reject the whole operation. Shape and collection names describe
the values actually returned.

Choose the outcome from the consumer's decisions. A guaranteed resolution returns its value. A
present-or-absent application resolution uses the selected optional carrier. Distinguishable expected
failures use the selected typed result. With Reunion, these are `T`, `Option<T>` and `Result<T, TError>`
respectively, as defined by [dotnet:result-carriers](../result-carriers/SKILL.md). This applies to the
resolver contract even when its implementation lives in an Infrastructure project.

## Validator contracts

A validator assesses an existing candidate and reports whether its rules hold. Name its operation
`Validate` or `Validate` plus the assessed intent, with `Async` for asynchronous work. An actual boolean
capability question uses `Can`, `Is` or `Has` and returns `bool`.

Projects selecting [dotnet:validation](../validation/SKILL.md) use that owner's separate input-shape
and domain-eligibility contracts, including their validation result types. Library-owned validator
methods retain their library signatures. A resolver may check candidate validity while returning a
resolved value; its useful result remains a resolution. Conversely, validation may load data while
returning a validation decision. Both implementation and returned contract establish the role.

## Construction and qualifiers

Use a named static creation method when the domain type owns its construction. Use a factory or
generator when callers consume a separate construction responsibility, a family of outputs, or
construction owned by an outer layer. Seed construction follows
[dotnet:seeding](../seeding/SKILL.md) when that profile is selected.

Qualifiers express real caller-visible distinctions: a primary or fallback strategy, a read capability,
a captured snapshot, or another domain distinction. Use the default role plainly. Concurrency
mechanisms remain named for their actual synchronization contract where those mechanisms are exposed;
application collaborators are named for the domain capability their callers consume.

## Review and refactoring

Review the interface, implementation, DI registration, result shape and production call site together.
A role change includes the responsibilities and dependencies that establish it. Moving a persistence
operation into an application collaborator also changes its boundary contract and invokes the selected
carrier rules. Preserve transaction, cancellation and authorization guarantees through that change.
Keep protocol-specific failure mapping at its owning boundary. Confirm that the resulting call reads
as the domain subject performing its operation and producing the documented outcome.
