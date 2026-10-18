---
name: persistence
description: EF Core persistence standard for a .NET service — repositories never leak `IQueryable`, `CancellationToken` on every async method that can reach I/O, schema and table names as constants rather than scattered string literals, awaiting a mapper's prefetch before projecting rather than per-row round trips, choosing between one `SaveChanges`, an explicit transaction and an ambient cross-context scope, never sharing a transaction across services, exactly one context migrating a table with every borrower mapping it through `ExcludeFromMigrations`, and no foreign key from a write model to a read model. Use when adding a repository or a query, configuring an entity, mapping a query result, or deciding how a write is committed.
kind: contract
domain: dotnet
profile: ef-core
applicability: projects using EF Core
requires: ef-core
provenance: library
---

# Persistence

Owns EF Core data-access practice: query surfaces, cancellation, table naming, commits and migrations.

## Applicability

This contract applies only to projects using EF Core. It requires `ef-core`. Installing `efcore@dotagents` makes this guidance available; it does not select those technologies for a consuming repository.

`efcore:specification` owns parameterized criteria; `efcore:query-building` owns injected query composition.
`dotnet:repositories` owns repository names, query and write verbs, storage return shapes and the boundary
to application collaborators. A product's own repository base hierarchy and unit-of-work types belong to
that product's standards.

## Repositories never leak `IQueryable`

Filtering, aggregation, and projection stay inside data access. Type-to-type conversion and cross-module
enrichment belong to the service and its `XMappers` class. A repository that returns `IQueryable` has
handed its caller an unbounded query surface tied to a live context. Internal builders may return deferred
queries to their owning repository under `efcore:query-building`; the repository materializes the result.

**Every async application-service and repository method that can reach I/O takes a
`CancellationToken ct = default`** and passes it to every awaited call that accepts one. Cancellation
propagates as cancellation; it is never converted into a Result.

## Schema and table names are constants

Name a persistence module's schema and its tables once, as `const string`s, and reference those constants
from the EF configurations, never a bare literal, so a renamed table changes one constant instead of N
scattered strings.

Columns need no equivalent: EF names each column after its property, so a configuration sets one only for a
deliberate rename (`HasColumnName("Period_Start")`), and those few stay inline literals rather than growing
a constants class.

## Await a mapper's prefetch, then project

A mapper is normally `async` because it prefetches a dependency in one batch, not because projecting a row is
asynchronous. Await the batch first, then project synchronously over the result. Awaiting *inside* the
selector is the real defect — that is a per-row round trip.

## Commit by the number of flushes and contexts

- One context and one flush, the default: stage every entity change, then save once; EF commits that save
  atomically.
- One context where the operation genuinely needs several `SaveChanges` calls, or needs its reads and writes
  to share one explicit transaction: run it inside one explicit transaction.
- Writes to several contexts inside one service, and only then: an ambient `TransactionScope`, because a
  single-context transaction cannot span them.

An expected write failure inside an ambient scope is classified only by the scope's owner, after rolling the
scope back, so the recovery runs against no transaction. A block that classifies the failure and returns
normally inside the scope still commits whatever the failed save's pre-commit handlers wrote to the other
enlisted contexts. Nested inside another scope, classify nothing and let the failure reach the root.

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

## Persisting seed state

```csharp
public async Task SeedAsync(CancellationToken ct)
{
    if (await context.Warehouses.AnyAsync(ct).ConfigureAwait(false)) return;
    context.Warehouses.AddRange(seedData.Warehouses);
    await context.SaveChangesAsync(ct).ConfigureAwait(false);
}
```

`dotnet:seeding` owns what may be seeded, canonical seed state and sentinel selection. This EF example
applies only when a whole-table guard is valid; event-created rows require the specific sentinel defined
by that contract.
