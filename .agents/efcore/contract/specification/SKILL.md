---
name: specification
description: Specification parameter objects in EF Core query pipelines — concrete immutable criteria, dependency-free construction per operation, expression composition and evaluator ownership. Use when adding or reviewing EF Core specifications, passing selection criteria to a query or repository, or replacing specifications registered in DI.
kind: contract
domain: dotnet
profile: ef-core
applicability: EF Core projects using reusable query specifications
requires: ef-core
provenance: library, house
---

# EF Core specifications

A specification describes a selection rule. Construct it as an ordinary per-operation object and pass it
as a parameter to the query/evaluator API. An injected service that resolves inputs and assembles a query
is a `QueryBuilder`, governed by `efcore:query-building`.

## Criteria are values, not services

A specification constructor captures the concrete values defining its rule: a normalized search term,
an id set, a UTC timestamp, or an already-created geographic point and radius. Its resulting predicate
or declared query shape stays stable for that operation. Copy caller-owned mutable collections; either
own immutable geometry or copy mutable inputs so later caller changes cannot alter deferred execution.

Do not register a specification in DI or give it dependencies such as `DbContext`, `TimeProvider`, a
geometry provider, tenant accessor, HTTP client or service provider. Resolve those inputs before
construction, normally in the injected query builder. Capture the current instant once per build;
a predicate must not read a moving clock during evaluation.

A specification is not a reusable service whose predicate accepts an entire request each time. Put the
specific rule's criteria in its constructor, keep them get-only/private, and pass the specification itself
to its consumer. Do not add an interface per leaf merely to inject it.

## Reuse the selected specification model

Use the repository's existing shared specification and evaluator API when it fits. Do not introduce a
second generic specification base, evaluator, or a new library per service. A product may choose a
predicate-only model or an established richer query specification model; the latter may describe includes,
ordering or projection as supported by its library. This contract does not require Ardalis.

In a predicate-only model, `ToExpression()` produces an `Expression<Func<TEntity, bool>>`; `And`, `Or`
and `Not` combine specifications. Rebind expression parameters through the selected shared composition
implementation. Avoid compiling a predicate to a delegate or using expression invocation that the selected
provider cannot translate. The evaluator applies the expression with `Where`; it does not resolve services
or decide request-specific criteria. `dotnet:naming-collaborators` owns the generic predicate role; an EF
`SpecificationEvaluator` is the library's query-application role rather than an application verdict service.

Keep projection, includes and ordering in the builder/evaluator layer when the selected model supports
predicates only. Filtering a count or existence query uses the same criteria while respecting its own
cardinality contract; do not accidentally apply page limits before counting.

An inactive optional criterion contributes the selected model's identity predicate (true for an `And`
chain), or the builder omits it. Empty input and null semantics must preserve the operation's declared
behavior. A set of specifications is request data, never a process-wide mutable cache.

## Verify the persistence behavior

Use provider-backed integration coverage for SQL translation, null/empty criteria, combined filters,
ordering and pagination where they affect this operation. Pure expression checks may supplement this,
but a LINQ-to-Objects test alone cannot establish EF translation or database semantics. Follow
`dotnet:testing` for the selected test tier; do not introduce a new test layer for this convention.

## Source and decision

Tommy, 2026-10-18: specifications are parameter objects rather than DI services; EF query conventions
live under `efcore` so their scope is visible. This retains the selected product abstraction instead of
adding another one.

[Ardalis constructs specifications from constructor criteria](https://specification.ardalis.com/usage/create-specifications.html)
and [applies them through a stateless evaluator](https://specification.ardalis.com/usage/use-specification-repository-pattern.html).
Those examples support the separation of description from application. Dependency-free per-operation
criteria and the naming above are the house convention; a specification pattern can also be used outside
EF Core.
