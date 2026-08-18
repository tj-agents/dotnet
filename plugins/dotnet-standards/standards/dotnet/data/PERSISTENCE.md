# Persistence

## A repository inherits its module's `Repository<T>` base

Every module owns a `Repositories/Repository.cs` binding the shared data-access bases to that module's
`DbContext` and key type:

```csharp
internal abstract class WriteRepository<TEntity>(OrderDbContext context)
    : WriteRepository<TEntity, OrderDbContext>(context)
    where TEntity : class;

internal abstract class Repository<TEntity>(OrderDbContext context)
    : Repository<TEntity, OrderDbContext, Guid>(context)
    where TEntity : class, IGuidEntity;
```

A concrete repository inherits that base and implements the module's `IXRepository`, which extends
`IRepository<XEntity, TKey>` and **needs no members of its own** unless the module has extra queries.
`GetAll`/`GetById`/`Exists`/`Add`/`Update`/`Remove`/`SaveChanges` all come from the base — **never
re-declare them**, not even a `CancellationToken` overload of `GetById`. Add only the extra finders the
base cannot express, querying through the inherited `context` field.

```csharp
internal interface IOrderRepository : IRepository<OrderEntity, Guid>;

internal sealed class OrderRepository : Repository<OrderEntity>, IOrderRepository
{
    public OrderRepository(OrderDbContext context) : base(context) { }
    // extra finders only — query via the inherited `context`
}
```

The injected context field is always named `context`, never `dbContext`. Do not hand-roll a bare
`IXRepository` that re-implements CRUD.

Naming — a repository method says what it fetches and by what key, a service method says the intent — is in
the `csharp-naming` skill, along with the `Projection` suffix rule.

## Repositories never leak `IQueryable`

Filtering, aggregation, and projection stay inside data access. Type-to-type conversion and cross-module
enrichment belong to the service and its `XMappers` class. A repository that returns `IQueryable` has
handed its caller an unbounded query surface and an open connection.

**Every async application-service and repository method that can reach I/O takes a
`CancellationToken ct = default`** and passes it to every awaited call that accepts one. Cancellation
propagates as cancellation; it is never converted into a Result.

## Schema and table names are module constants

Each persistence module owns a `Schema.cs` (`internal static class Schema`) holding its schema name and its
table names as `const string`s — `Schema.Name`, `Schema.Tables.Invoices`. EF configurations reference those
constants (`builder.ToTable(Schema.Tables.Invoices, Schema.Name)`), never a bare literal, so a renamed table
changes one constant instead of N scattered strings.

Columns need no equivalent: EF names each column after its property, so a configuration sets one only for a
deliberate rename (`HasColumnName("Period_Start")`), and those few stay inline literals rather than growing
a constants class.

## Project a page with `Map`

```csharp
return (await reportRepository.GetQueueAsync(pageParams)).Map(r => r.ToDto());
```

`Map` carries `TotalCount`/`PageNumber`/`PageSize` across, so hand-writing `new Pagination<T>(...)` restates
four arguments that have exactly one correct value. One case is **not** `Map`: **only the item type widens** —
`IPagination<out T>` is covariant, so an `IPagination<ArtistHeader>` already *is* an `IPagination<IHeader>`.
Return it; don't re-wrap, and don't `Map(x => x)`.

**An `async` mapper is not an exception.** A mapper is normally `async` because it prefetches a dependency in
one batch, not because projecting a row is asynchronous. Await the batch first, then `Map` synchronously over
the result:

```csharp
var deals = await DealsByIdAsync(page.Data);
return page.Map(item => ToDto(item, deals));
```

Awaiting *inside* the selector is the real defect anyway — that is a per-row round trip.

## Unit of work — choose by the number of flushes and contexts

- **`IUnitOfWork<T>.SaveChangesAsync()`** — the default for one context and one flush. Stage every entity
  change, then save once; EF commits that save atomically.
- **`IUnitOfWork<T>.ExecuteAsync(block)`** — one context where the operation genuinely needs several
  `SaveChanges` calls, or needs its reads and writes to share one explicit transaction.
- **`IUnitOfWorkBehavior<T>.ExecuteAsync(block)`** — cross-module only. Wraps the block in an ambient
  `TransactionScope` so writes to several modules' contexts inside one service enlist in one transaction; a
  single-context transaction cannot span them.

**Never share a transaction across services.** A separate service owns its own database — coordinate those
with messages through an outbox, never a unit of work.

## Write models never carry an FK to a read model

A navigation property from a write entity to a read-model projection creates a database foreign key from the
write table to the read table, which couples the write model's persistence to the read model's availability
and fails while the read table is still empty. If you find
`HasOne(o => o.XReadModel).WithMany().HasForeignKey(o => o.XId)` in a configuration, remove the FK and the
navigation property; `XId` stays a plain column with no constraint.
