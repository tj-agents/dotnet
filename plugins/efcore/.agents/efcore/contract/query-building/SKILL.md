---
name: query-building
description: Injected EF Core QueryBuilder services that resolve concrete inputs, compose specifications and return deferred IQueryable queries for a repository to execute, with explicit dependency lifetimes and no retained operation state. Use when adding, naming, registering or reviewing a DI query builder or separating query composition from specification criteria and materialization.
kind: contract
domain: dotnet
profile: ef-core
applicability: EF Core projects extracting query composition into injected collaborators
requires: ef-core
provenance: library, house
---

# EF Core query building

Use `<Subject>QueryBuilder`, with `Build(source, parameters)`, for an injected collaborator whose job is
to compose an EF query. An interface, when the application needs one, is `I<Subject>QueryBuilder`.
Reuse the product's shared query-builder contract; do not invent a generic base or interface per service.
`DI` describes construction, not the class's name or responsibility.

## Roles and operation flow

| Role | Input and output | Lifetime and owner |
|---|---|---|
| Specification | Concrete criteria to stable predicate/query description | Constructed per operation; `efcore:specification` |
| Query builder | Source `IQueryable<TEntity>` and operation parameters to composed `IQueryable<TEntity>` | Injected service; owns input resolution and query composition |
| Specification evaluator | Source and specification to filtered/shaped query | Selected shared/library adapter; no request-specific input resolution |
| Repository | Operation input to materialized storage result | Owns context, execution, cancellation and storage boundary; `efcore:persistence` |

The builder resolves concrete values from its injected dependencies, creates fresh specifications, composes
them using the selected shared API, and applies them through the selected evaluator. It adds joins,
projection and ordering as required by the operation. For example, a builder reads the clock once and
creates a temporal specification from that instant; it resolves geometry through the selected provider
and gives the geographic specification the resulting point and radius. The specification never receives
the clock or provider.

Keep `Build` synchronous when it only composes an expression and uses synchronous dependencies. Inputs
requiring I/O must be resolved through the owning asynchronous operation with cancellation before this
composition; never block on a task inside `Build`. A service that executes a query and returns rows has an
execution responsibility, and follows repository/application naming rather than claiming to only build.

## Deferred execution stays inside data access

Accept the source explicitly and preserve its EF provider. Do not call `ToList`, `AsEnumerable`, `Compile`
or a terminal async method inside a composition-only builder. Do not turn fetched rows back into
`IQueryable` to resemble the EF contract. Materialization belongs to the repository, while its context
is alive, and the repository propagates cancellation to EF's terminal operation.

The internal `IQueryable` return is intentional: it stays between data-access collaborators. An application
service or HTTP caller receives the declared materialized result, not the query. Match the existing
operation's tracking stance, projection, count semantics and page boundaries. Paging needs a deterministic
ordering with a unique tie-breaker when the selected primary order can tie.

## DI lifetime follows dependencies

A builder stores dependencies only. It never stores the source query, request, specifications, current time,
geometry or other operation state in fields between builds. Resolve keyed dependencies explicitly when
the product selects them. Register only the builder and supporting services; remove leaf specification
interfaces and registrations that existed only to inject parameterized rules.

A singleton builder is valid only when it is thread-safe and all dependencies are singleton-safe.
It must not capture a scoped `DbContext`, tenant/request accessor or another scoped dependency. A builder
that genuinely requires a scoped dependency is scoped. Passing a context-backed source to a stateless
singleton method does not let the builder retain it, use it concurrently or outlive the owning operation.
Use `dotnet:dependency-injection` for registration conventions.

## Naming evidence

`QueryBuilder` / `Build` is a descriptive house convention, not a Microsoft-defined extension point.
Microsoft calls the LINQ infrastructure [`IQueryProvider`](https://learn.microsoft.com/en-us/dotnet/api/system.linq.iqueryprovider);
reserve that name for actual provider implementations. `Query` alone may mean a request, an expression
or an executable operation, so it does not communicate this collaborator's composition-only role.

[Microsoft explains deferred EF query execution](https://learn.microsoft.com/en-us/ef/core/querying/how-query-works)
and [the short-lived, non-thread-safe DbContext](https://learn.microsoft.com/en-us/ef/core/dbcontext-configuration/).
Those facts motivate the execution/lifetime boundary. [Ardalis's evaluator example](https://specification.ardalis.com/usage/use-specification-repository-pattern.html)
demonstrates applying a description to a source without putting request resolution in the specification.

Tommy, 2026-10-18: canonical query-building guidance accompanies the specification parameter-object
convention under the EF Core namespace. The role name is chosen for what the service returns.
