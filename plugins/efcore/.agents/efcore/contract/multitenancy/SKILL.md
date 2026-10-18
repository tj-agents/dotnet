---
name: multitenancy
description: Multi-tenant EF Core standard — visibility comes from what a context is composed from, never from disabling a filter per query (`IgnoreQueryFilters` banned via `RS0030`), one data-access stance per query class, declaring a filter per entity rather than deriving it from a marker interface, and filtering only where an entity's *reads* are tenant-private. Use when adding a `DbContext` or a repository to a tenant-aware module, deciding whether an entity should be query-filtered, hitting data that a filter is hiding, or reviewing any code that wants to bypass a global query filter.
kind: contract
domain: dotnet
profile: multitenancy
applicability: multi-tenant projects using EF Core
requires: ef-core, multitenancy
provenance: library, architecture
---

# Multitenancy

Owns multi-tenant EF Core visibility — composed stances, stance separation and filter declarations.

```csharp
public sealed class PrivateOrderConfiguration : IEntityTypeConfiguration<PrivateOrder>
{
    private readonly PrivateReadDbContext context;

    public PrivateOrderConfiguration(PrivateReadDbContext context)
    {
        this.context = context;
    }

    public void Configure(EntityTypeBuilder<PrivateOrder> builder) =>
        builder.HasQueryFilter(order => order.TenantId == context.TenantId);
}
```

The private-read context exposes its tenant value; its established context-capability model composition
applies this per-entity configuration. Keep `OnModelCreating` with the owning base. A separate public-read
context uses its deliberate tenant-independent map, rather than subtracting this private filter per query.
The predicate references the current context's tenant, not a tenant id frozen into a shared model.


## Applicability

This contract applies only to multi-tenant projects using EF Core. It requires `ef-core, multitenancy`. Installing `efcore@dotagents` makes this guidance available; it does not select those technologies for a consuming repository.

A product's concrete stance classes, their registration and its repository qualifier vocabulary belong to
that product's standards.

## Visibility is composed, never subtracted

Visibility comes from **what a context is built from**, not from disabling rules after the fact.
Per-query `IgnoreQueryFilters` is banned: "add a global rule, then remove it for half the callers" hides
the stance at every call site and is unauditable. Enforce it mechanically — add `IgnoreQueryFilters` to a
`BannedSymbols.txt` with `BannedApiAnalyzers` and `RS0030 = error` — so the codebase cannot accumulate
exceptions.

## One data-access stance per query class

Mixing stances in one class is the Liskov violation — a caller cannot know which contract a given method
honours.

## Declare filters per entity, and only where reads are tenant-private

Never auto-derive filters from a tenant marker interface. The marker means "carries the owner id", not "is
filtered" — marked ≠ filtered is a per-entity product decision.

**Filter an entity only when its *reads* are tenant-private.** If the entity's core flow reads it *across*
tenants, leave it unfiltered and let a write-side interceptor that stamps the tenant guard the writes;
filtering it fails those cross-tenant reads closed, silently. A public listing read by anonymous visitors,
or a counterparty's terms read by the party responding to them, are unfiltered by design. Owner-private
reads are filtered, with any public browse split off to a tenant-independent read context.
