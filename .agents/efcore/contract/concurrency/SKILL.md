---
name: concurrency
description: EF Core concurrency standard — optimistic concurrency tokens by default with `DbUpdateConcurrencyException` as the expected conflict, multi-row invariants versioned or locked on the aggregate root, pessimistic row locks only for short hard-to-retry transactions, taken as raw SQL in the owning repository in the weakest mode that holds, a fixed lock order, the execution strategy around a locking transaction, and advisory locks named as acquisitions. Use when two writers can race on the same rows, adding a concurrency token, reaching for `FOR UPDATE`/`FOR SHARE`, fencing a delete, or handling `DbUpdateConcurrencyException`.
kind: contract
domain: dotnet
profile: ef-core
applicability: projects using EF Core
requires: ef-core
provenance: library
---

# Concurrency

Owns EF Core write concurrency: optimistic tokens, conflict handling, pessimistic row locks and advisory locks.

## Applicability

This contract applies only to projects using EF Core. It requires `ef-core`. Installing `efcore@tj-agents` makes this guidance available; it does not select those technologies for a consuming repository.

`dotnet:repositories` owns lock method names; `dotnet:structure-modules` owns which module may lock which rows;
`efcore:persistence` owns commits and transaction scope.

## Concurrency is optimistic by default

```csharp
builder.Property(membership => membership.Version).IsConcurrencyToken();

try
{
    await context.SaveChangesAsync(ct);
}
catch (DbUpdateConcurrencyException)
{
    return MembershipErrors.Superseded;
}
```

Protect a contended write with a concurrency token (on PostgreSQL, Npgsql's `xmin`) and translate
`DbUpdateConcurrencyException` into the operation's expected conflict result. An invariant spanning several rows
is protected on its aggregate root: version the root, or lock it, so every writer of the invariant contends on
one row.

Why: EF Core ships optimistic concurrency and no lock API; a token costs nothing until two writers actually race.
Sources: [EF concurrency](https://learn.microsoft.com/en-us/ef/core/saving/concurrency),
[Npgsql concurrency](https://www.npgsql.org/efcore/modeling/concurrency.html).

## A row lock is taken in the owning repository

```csharp
public Task<TenantEntity?> GetByIdWithKeyShareLockAsync(Guid tenantId, CancellationToken ct = default) =>
    context.Tenants
        .FromSql($"""SELECT * FROM tenant."Tenants" WHERE "Id" = {tenantId} FOR KEY SHARE""")
        .SingleOrDefaultAsync(ct);
```

Take a pessimistic row lock only for a short transaction that is hard to retry, in the repository of the
module that owns the rows, never in a service, handler or another module's repository. Where the product's
shared data-access layer provides a query-level lock operator, use it instead of `FromSql`, so no consumer
writes lock SQL or table names. Lock, then load in a separate statement: a locking query that joins returns
stale joined rows after a lock wait, because PostgreSQL rechecks only the locked row. Use
the weakest mode that holds the invariant: `FOR KEY SHARE` fences a delete or key change, `FOR NO KEY UPDATE`
serializes ordinary updates, `FOR UPDATE` only when the transaction deletes the row or changes its key. Encode the lock order inside the
repository that takes several locks, so no caller can acquire them in another order.

When the context enables retries, run the locking transaction inside
`context.Database.CreateExecutionStrategy().ExecuteAsync`, so a retry replays the whole transaction rather than
a statement inside it.

Why: a lock outside the owning repository is a lock nobody else knows to take, and a stronger mode than needed
blocks writers the invariant never concerned.
Sources: [dotnet/efcore#26042](https://github.com/dotnet/efcore/issues/26042),
[PostgreSQL explicit locking](https://www.postgresql.org/docs/current/explicit-locking.html),
[EF connection resiliency](https://learn.microsoft.com/en-us/ef/core/miscellaneous/connection-resiliency),
[Fowler, Implicit Lock](https://martinfowler.com/eaaCatalog/implicitLock.html).

## An advisory lock is acquired, never named like a row lock

```csharp
public Task AcquireInvoiceNumberLockAsync(Guid tenantId, CancellationToken ct = default) =>
    context.Database.ExecuteSqlAsync($"SELECT pg_advisory_xact_lock(hashtext({tenantId.ToString()}))", ct);
```

An advisory lock guards a resource that is not a row, such as a number sequence. Name it
`Acquire<Resource>LockAsync` and take the transaction-scoped form so commit or rollback releases it.

Why: a `…ForUpdate` name promises a locked row the caller can read; an advisory lock returns none.
Sources: [PostgreSQL advisory locks](https://www.postgresql.org/docs/current/explicit-locking.html#ADVISORY-LOCKS).
