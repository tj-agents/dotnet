---
name: persistence
description: EF Core persistence standard for a .NET service — the context-capability triple that decides which shared base a repository inherits, the per-module `Repository<T>` alias that binds it to that module's `DbContext` and key type, the matching module-local aliases for every unit-of-work carrier (aliased as a set, never registered as an open generic), concrete repositories that add only the finders the base cannot express, never re-declaring inherited CRUD, the `context` field name, one repository per entity, `InsertAsync` rather than `AddAsync` plus `SaveChangesAsync` when nothing else is staged, repositories that never leak `IQueryable`, schema and table names as module constants rather than scattered string literals, `CancellationToken` on every async method that can reach I/O, projecting a page with `IPagination<T>.Map` instead of reconstructing it, and choosing between a single `SaveChanges`, an explicit transaction, and an ambient cross-module scope. Use when adding a repository or a query, choosing a base or alias, staging a write, configuring an entity, mapping a paged result, or deciding how a write is committed.
kind: contract
domain: dotnet
profile: ef-core
applicability: projects using EF Core and the selected repository/unit-of-work abstractions
requires: ef-core, selected-data-access-abstractions
provenance: library, selected-stack, house
---

# Persistence

Owns the EF Core repository base hierarchy, aliasing, writes and the unit-of-work carriers.

## Applicability

This contract applies only to projects using EF Core and the selected repository/unit-of-work abstractions. It requires `ef-core, selected-data-access-abstractions`. Installing `dotnet@dotagents` makes this guidance available; it does not select those technologies for a consuming repository.

## A repository binds to a context capability, not to a concrete context type

The shared data-access layer mirrors the context capability hierarchy in its repository hierarchy, one row
per capability:

```text
IReadDbContext  -> IReadRepository<TEntity, TKey>  -> ReadRepository<TEntity, TKey>
IWriteDbContext -> IWriteRepository<TEntity>       -> WriteRepository<TEntity>
IDbContext      -> IRepository<TEntity, TKey>      -> Repository<TEntity, TKey>
```

The row decides which base a repository inherits: a read-stance repository takes the read triple, not the
full one. The shared bases deliberately take **no concrete `TContext` generic parameter** — their protected
`Context` property exposes the capability alone, so a repository cannot reach past its own stance.

Every module owns a `Repositories/Repository.cs` holding the local alias that binds its concrete context and
key type, and concrete repositories in that module derive from the alias:

```csharp
internal abstract class Repository<TEntity>(OrderDbContext context)
    : Repository<TEntity, Guid>(context)
    where TEntity : class, IGuidEntity;
```

Add a module-local `ReadRepository<TEntity>` / `WriteRepository<TEntity>` alias only when concrete
repositories actually derive from it.

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
`IXRepository` that re-implements CRUD. Keep the concrete context in a `private readonly` field only when
the repository genuinely needs typed `DbSet`s or `Entry`/`Database`/`ChangeTracker`/bulk operations.

## Adding one entity with nothing else staged — `InsertAsync`, not `AddAsync` + `SaveChangesAsync`

`IWriteRepository<TEntity>` gives both. `AddAsync` stages only, for a unit of work that stages several
writes before one shared save; `InsertAsync` stages *and* saves. Reach for the two-call form only when
something else is already staged in the same method and the save commits all of it together.

## One repository per entity — never fold a satellite entity into another entity's repository

A repository's generic base binds it to exactly one entity. Give every entity its own repository even when
several share a module and a `DbContext`, and even when one is queried far more often than another.
Repository counts therefore run *ahead* of entity counts rather than tracking them, because stance and
projection shape are independent dimensions — a separate read stance, an admin stance and a read-model
repository each earn their own.

The tell that a repository has drifted: its interface mixes queries for two or more unrelated entity types,
or it hand-writes a `GetXByIdAsync`/`AddX` pair that re-implements what the generic base already gives the
*wrong* entity bound as `TEntity`. Split it — one interface, one repository, one entity — even if a single
service then injects two repositories. That is the service's job, not a reason to merge the persistence
contracts.

## Repository contracts

`dotnet:naming-repositories` owns entity/capability names, query and write
verbs, storage return shapes, visibility composition and the boundary to application collaborators.
Apply it together with this selected EF Core implementation contract. Module-local aliases bind the
exposed capability to the corresponding context triple described above; the context's wider capability
preserves the narrower interface's contract.

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
`IPagination<out T>` is covariant, so an `IPagination<SellerHeader>` already *is* an `IPagination<IHeader>`.
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

Every generic carrier a module uses is aliased once, in the module, exactly as `Repository<TEntity>` is —
`IUnitOfWork`, `IUnitOfWorkBehavior`, `IOutboxUnitOfWorkBehavior`, `IUnitOfWorkBoundary`. The alias binds the
module's concrete context so nothing downstream ever spells the closed generic again:

```csharp
internal interface IUnitOfWork : DataAccess.Application.IUnitOfWork<OrderDbContext>;

internal sealed class UnitOfWork(OrderDbContext context)
    : DataAccess.Infrastructure.UnitOfWork<OrderDbContext>(context), IUnitOfWork;
```

```csharp
services.AddScoped<IUnitOfWork, UnitOfWork>();
services.AddScoped<IUnitOfWorkBehavior, UnitOfWorkBehavior>();
```

**Alias the whole set or none of it.** A module that aliases `IUnitOfWorkBehavior` but registers
`IUnitOfWork<XDbContext>` open has two vocabularies for one context, and the second consumer picks the wrong
one. Registering an open generic where the module owns an alias is the defect.


- **`IUnitOfWork<T>.SaveChangesAsync()`** — the default for one context and one flush. Stage every entity
  change, then save once; EF commits that save atomically.
- **`IUnitOfWork<T>.ExecuteAsync(block)`** — one context where the operation genuinely needs several
  `SaveChanges` calls, or needs its reads and writes to share one explicit transaction.
- **`IUnitOfWorkBehavior<T>.ExecuteAsync(block)`** — cross-module only. Wraps the block in an ambient
  `TransactionScope` so writes to several modules' contexts inside one service enlist in one transaction; a
  single-context transaction cannot span them.
- **`IUnitOfWorkBehavior<T>.TryExecuteAsync(block, isExpected, onExpectedFailure)`** — the same ambient
  scope when a write failure is expected. It rolls the scope back before classifying, so the recovery runs
  against no transaction.

**Never classify an expected failure with `TrySaveChangesAsync` inside an ambient scope.** A block that
returns normally commits that scope, so a failure swallowed inside it still commits whatever the failed
save's pre-commit handlers wrote to the other enlisted contexts. Only the scope's owner can roll back:
nested inside another scope `TryExecuteAsync` classifies nothing and lets the failure reach the root.

**Never share a transaction across services.** A separate service owns its own database — coordinate those
with messages through an outbox, never a unit of work.

## Exactly one context migrates a table — everyone else maps it with `ExcludeFromMigrations`

A module often needs to read a table another module owns: a rating projection to join against, the outbox
and inbox rows a shared base maps into every context. Map it in the borrowing context, and exclude it from
that context's migrations, so the schema has exactly one author:

```csharp
// in the BORROWING module's configuration - read-only, never migrated from here
builder.ToTable("SellerRatingProjections", "seller", t => t.ExcludeFromMigrations());
```

The owning module maps the same table with **no** exclusion; its migration is the one that creates it.
Omitting the exclusion in the borrower is not a duplicate mapping you get away with — it is two
migrations both claiming the table, one of which will fail against a database the other already built.

**Borrowed means read-only.** Map it, key it, query it; do not write through it or add a foreign key to
it — the owning module's writes are the only ones the projection's invariants know about.

## Write models never carry an FK to a read model

A navigation property from a write entity to a read-model projection creates a database foreign key from the
write table to the read table, which couples the write model's persistence to the read model's availability
and fails while the read table is still empty. If you find
`HasOne(o => o.XReadModel).WithMany().HasForeignKey(o => o.XId)` in a configuration, remove the FK and the
navigation property; `XId` stays a plain column with no constraint.
