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

Owns injected EF Core query composition, deferred execution boundaries and builder dependency lifetimes.

```csharp
public sealed record ReadyOrdersParameters(IReadOnlyCollection<Guid> Ids);

public sealed class OrderQueryBuilder
{
    private readonly TimeProvider timeProvider;

    public OrderQueryBuilder(TimeProvider timeProvider)
    {
        this.timeProvider = timeProvider;
    }

    public IQueryable<Order> Build(IQueryable<Order> source, ReadyOrdersParameters parameters)
    {
        var asOf = timeProvider.GetUtcNow();
        IPredicateSpecification<Order> specification = new ReadyOrdersSpecification(parameters.Ids, asOf);

        return source.Where(specification.ToExpression())
            .OrderBy(order => order.ReadyAt)
            .ThenBy(order => order.Id);
    }
}
```

This continues `efcore:specification`'s Order example. The injected builder reads the clock once, constructs
fresh criteria, applies their expression and adds deterministic ordering with an id tie-breaker. `Where`
is the query-application step here; use the selected shared evaluator when that API owns application.
Reuse an existing shared builder interface when the product has one; no new generic framework is implied.

Use `<Subject>QueryBuilder` / `Build(source, parameters)` for this composition-only collaborator. It is a
house recommendation: the research found no universally accepted name for this exact DI role. Reserve
[`IQueryProvider`](https://learn.microsoft.com/en-us/dotnet/api/system.linq.iqueryprovider) for LINQ provider
infrastructure. `DI` describes how the service is constructed, not its responsibility or class name.

The builder's query-building logic is reusable across calls. Each returned `IQueryable` is a new deferred,
context-bound expression for that operation; never retain it, its source, request, specifications or resolved
values in the service's fields. Preserve the EF provider: no `ToList`, `AsEnumerable`, compiled delegates,
blocking I/O or terminal async operation inside `Build`. Resolve inputs requiring I/O in the owning async
operation with cancellation before calling synchronous composition.

```csharp
public sealed class OrderRepository
{
    private readonly OrderDbContext context;
    private readonly OrderQueryBuilder queryBuilder;

    public OrderRepository(OrderDbContext context, OrderQueryBuilder queryBuilder)
    {
        this.context = context;
        this.queryBuilder = queryBuilder;
    }

    public async Task<IReadOnlyList<Order>> GetReadyAsync(
        ReadyOrdersParameters parameters, CancellationToken ct = default) =>
        await queryBuilder.Build(context.Orders.AsNoTracking(), parameters)
            .ToListAsync(ct).ConfigureAwait(false);
}
```

The repository supplies its live context's source and materializes the query with cancellation. The
application receives rows; the deferred `IQueryable` stays inside data access (`efcore:persistence`).
Preserve the operation's tracking, projection and count/page semantics when extending the builder.

```csharp
public static class OrderServices
{
    public static IServiceCollection AddOrderQueries(
        this IServiceCollection services, Action<DbContextOptionsBuilder> configureDatabase)
    {
        services.AddSingleton(TimeProvider.System);
        services.AddSingleton<OrderQueryBuilder>();
        services.AddDbContext<OrderDbContext>(configureDatabase);
        services.AddScoped<OrderRepository>();
        return services;
    }
}
```

`configureDatabase` supplies the application's selected EF provider. `AddDbContext` registers the context
as scoped; the repository shares that scope. This builder can be singleton because it stores only the
thread-safe singleton clock. A builder needing a scoped dependency is scoped instead. Never capture a
scoped context, request/tenant accessor or a context-backed query in a singleton. Passing the source into
`Build` does not permit retaining it or concurrently using the context. Register builders and dependencies,
not leaf specifications; use `dotnet:dependency-injection` for registration conventions.

[Microsoft documents deferred execution](https://learn.microsoft.com/en-us/ef/core/querying/how-query-works)
and [short-lived, non-thread-safe contexts](https://learn.microsoft.com/en-us/ef/core/dbcontext-configuration/).
Those facts establish the composition/execution boundary; [Ardalis's evaluator example](https://specification.ardalis.com/usage/use-specification-repository-pattern.html)
illustrates applying criteria without placing service resolution inside them.

Tommy, 2026-10-18: canonical EF query-building guidance accompanies constructor-bound specifications.
The examples make the house role name, input ownership and DI lifetime concrete.
