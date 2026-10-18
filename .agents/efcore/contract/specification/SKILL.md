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

```csharp
public sealed class ReadyOrdersSpecification : PredicateSpecification<Order>
{
    private readonly Guid[] ids;
    private readonly DateTimeOffset asOf;

    public ReadyOrdersSpecification(IEnumerable<Guid> ids, DateTimeOffset asOf)
    {
        this.ids = ids.ToArray();
        this.asOf = asOf;
    }

    protected override Expression<Func<Order, bool>> Predicate =>
        order => ids.Contains(order.Id) && order.ReadyAt <= asOf;
}
```

This example uses the selected shared `PredicateSpecification<TEntity>` / `IPredicateSpecification<TEntity>`
contract: `ToExpression()` exposes the predicate for query application. `Order` has `Guid Id` and
`DateTimeOffset ReadyAt`. Empty ids match no orders. The constructor copies caller-owned ids and captures
a concrete instant, so changes to the input collection or clock cannot change this operation's criteria.
Use the existing shared contract; do not add this base/interface or another specification library to a service.

Construct a specification per operation and pass it to the selected query/evaluator API. It is an ordinary
criteria object, never a DI registration. Do not inject `DbContext`, `TimeProvider`, geometry providers,
tenant accessors or other services into it. The builder resolves their values before construction;
`efcore:query-building` continues this same Order example. Mutable geometry needs the same ownership or
copying discipline as collections. Keep captured criteria private/get-only.

Compose predicates with the selected shared `And`, `Or` and `Not` API, which rebinds expression parameters.
Do not compile predicates to delegates or introduce invocation nodes the selected EF provider cannot
translate. The evaluator applies the description; it does not resolve request inputs. A library's
`SpecificationEvaluator` names this query adapter, distinct from an application verdict evaluator under
`dotnet:naming-collaborators`.

A predicate-only model leaves includes, projection and ordering with the query builder. A selected richer
library may describe them in its specification. Preserve declared null/empty semantics: an omitted optional
filter is either absent or an identity predicate, while this example's empty id set intentionally matches
nothing. Count/existence operations reuse criteria without accidentally applying page limits.

Check provider translation and database behavior in the selected integration tier (`dotnet:testing`).
LINQ-to-Objects checks alone cannot establish EF translation, null semantics or paging behavior.

Tommy, 2026-10-18: specifications are constructor-bound parameter objects rather than DI services; the EF
query convention has an `efcore` owner. [Ardalis constructor criteria](https://specification.ardalis.com/usage/create-specifications.html)
and [stateless evaluation](https://specification.ardalis.com/usage/use-specification-repository-pattern.html)
support that separation without requiring Ardalis. Specifications can also be used outside EF Core.
