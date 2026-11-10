---
name: unit-of-work
description: Use when a .NET use case stages writes, owns a commit or executes work in a transaction/retry envelope within one service.
kind: contract
domain: dotnet
profile: core
applicability: C# projects that persist state, regardless of persistence library
requires: none
provenance: pattern, house
---

# Unit of work

Owns who stages, who commits, and the envelope a commit runs in.

```csharp
public interface IUnitOfWork
{
    Task SaveChangesAsync(CancellationToken ct = default);

    Task<T> ExecuteAsync<T>(Func<CancellationToken, Task<T>> work, CancellationToken ct = default);
}
```

Repositories and the outbox publisher stage changes in the unit of work; the use case commits once with
`SaveChangesAsync`, so the state change and its outbox rows commit or roll back together. `ExecuteAsync` runs
caller-supplied work inside the envelope it owns — transaction bracket, retry, scope — and holds no business
logic. A unit of work covers one service's database; other services learn of the change through the outbox.

With EF Core the `DbContext` is the unit of work, and several flushes or contexts follow `efcore:persistence`.

Sources: [Fowler, Unit of Work](https://martinfowler.com/eaaCatalog/unitOfWork.html), dotnet/eShop
`IUnitOfWork`, EF Core [`IExecutionStrategy`](https://learn.microsoft.com/en-us/ef/core/miscellaneous/connection-resiliency).
