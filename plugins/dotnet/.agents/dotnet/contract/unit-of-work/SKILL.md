---
name: unit-of-work
description: The unit of work for a .NET service, independent of an ORM — repositories and the outbox stage changes, the use case commits once through `IUnitOfWork.SaveChangesAsync`, `ExecuteAsync` runs caller-supplied work inside the transaction envelope, and one unit of work covers one service's database. Use when committing, opening a transaction, wrapping work in a retry or transaction envelope, or deciding who saves.
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
