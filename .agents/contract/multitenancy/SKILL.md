---
name: multitenancy
description: Multi-tenant EF Core standard — visibility comes from what a context is composed from, never from disabling a filter per query (`IgnoreQueryFilters` banned via `RS0030`), the anemic per-module configuration provider that every stance composes, the tenant-scoped / read-only / privileged-writable context stances and the verbatim shape of each (bases own `OnModelCreating`; a read context exposes named `IQueryable`s through an explicitly-implemented `IXReadDbContext` that never extends `IReadDbContext` and must have a production consumer), the uniform DI registration of a stance, the per-module stance test, one data-access stance per query class, declaring a filter per entity rather than deriving it from a marker interface, filtering only where an entity's *reads* are tenant-private, and the independent naming dimensions (stance, mutability, projection shape) for repository qualifiers. Use when adding a `DbContext` or a repository to a tenant-aware module, wiring a context into DI, deciding whether an entity should be query-filtered, hitting data that a filter is hiding, or reviewing any code that wants to bypass a global query filter.
kind: contract
domain: dotnet
profile: multitenancy
applicability: multi-tenant projects using EF Core
requires: ef-core, multitenancy
provenance: library, architecture, house
---

# Multitenancy

## Applicability

This contract applies only to multi-tenant projects using EF Core. It requires `ef-core, multitenancy`. Installing `dotnet@dotagents` makes this guidance available; it does not select those technologies for a consuming repository.

## Visibility is composed, never subtracted

Visibility comes from **what a context is built from**, not from disabling rules after the fact.
Per-query `IgnoreQueryFilters` is banned: "add a global rule, then remove it for half the callers" hides
the stance at every call site and is unauditable. Enforce it mechanically — add `IgnoreQueryFilters` to a
`BannedSymbols.txt` with `BannedApiAnalyzers` and `RS0030 = error` — so the codebase cannot accumulate
exceptions.

The building blocks, all in the service's data-access infrastructure:

- **The module's `XConfigurationProvider` is the anemic core** — pure table mappings, zero tenancy. Every
  stance below composes it; none of them modifies it. **Every stance is per module.** A cross-module
  "sees everything" context is the monolith query surface module isolation exists to prevent.
- **`TenantScopedDbContext`** (abstract) — the tenant-filtered stance. It constructor-injects the module's
  configuration provider plus the ambient tenant context; its sealed `OnModelCreating` composes the anemic
  core first, then the module's filter declarations through an abstract `ApplyTenantFilters` hook.
- **`XReadDbContext`** (one concrete read context per module that needs one) — the tenant-independent read
  stance, composing the configuration provider with no tenancy on top. **Read-only by construction:**
  `SaveChanges` throws, so the write-side tenant interceptor can never be bypassed through it.
- **`PrivilegedDbContext`** (abstract) — the unfiltered **writable** stance, so a cross-tenant operator can
  act on rows it does not own; the interceptor's write guard no-ops for a tenant-less write. A module with
  no tenant-scoped entity at all takes this base too — there, "privileged" degenerates to "nothing to
  filter". Do not call it `AdminDbContext`: that name reads as the Admin *module's* context, a different
  thing entirely.

## The concrete context is `DbSet`s, filters and nothing else

The base owns `OnModelCreating` — default schema, then the provider, then filters, in that sealed order. **A
concrete context never declares `OnModelCreating`.** Modules hand-rolling those two lines is how one of them
silently drifts off its stance.

**Tenant-filtered** — a `DbSet` per entity, and `ApplyTenantFilters` naming only the entities whose reads are
tenant-private:

```csharp
internal sealed class OrderDbContext(
    DbContextOptions<OrderDbContext> options,
    OrderConfigurationProvider provider,
    ITenantContext tenantContext)
    : TenantScopedDbContext(options, provider, tenantContext, Schema.Name)
{
    public DbSet<OrderEntity> Orders => Set<OrderEntity>();
    public DbSet<OrderLineEntity> OrderLines => Set<OrderLineEntity>();

    protected override void ApplyTenantFilters(ModelBuilder modelBuilder) =>
        modelBuilder.ApplySingleOwner<OrderEntity>(this);
}
```

**Tenant-independent read** — a named `IQueryable` per entity, implemented *explicitly* against the module's
own read interface. No `DbSet`, no public member:

```csharp
internal interface IOrderReadDbContext
{
    IQueryable<OrderEntity> Orders { get; }
}

internal sealed class OrderReadDbContext(
    DbContextOptions<OrderReadDbContext> options,
    OrderConfigurationProvider provider)
    : ReadDbContext(options, provider, Schema.Name), IOrderReadDbContext
{
    IQueryable<OrderEntity> IOrderReadDbContext.Orders => Query<OrderEntity>();
}
```

`IXReadDbContext` deliberately does **not** extend `IReadDbContext`. The two are not general and specific:
the shared contract *is* the open `Query<TEntity>()`, so extending it would make the module's interface
**wider**, handing every consumer a query over every entity the module's provider maps — including the ones
an aggregate repository owns. Restriction is the whole job of the interface, and a restriction never
inherits the capability it restricts, for the same reason `IReadOnlyList<T>` does not extend `IList<T>`. The
concrete context still satisfies `IReadDbContext` through its base, which is what the shared read-repository
bases bind to. Implement the properties explicitly so the surface is reachable only through the interface.

**The interface earns its place from a production consumer** — an `XReadRepository`, or a purpose-named
abstraction over a domain fact. A test fixture resolving the read stance for unfiltered assertions is the
normal pattern and justifies the *context*; it does not justify the *interface*, which exists to narrow what
a production consumer can reach. With no such consumer there is nothing to narrow, so resolve the concrete
context in the fixture and add the interface when the first one arrives.

**Unfiltered and writable** — same provider, no tenancy, `DbSet`s public because the writer needs them:

```csharp
internal sealed class OrderModerationDbContext(
    DbContextOptions<OrderModerationDbContext> options,
    OrderConfigurationProvider provider)
    : PrivilegedDbContext(options, provider, Schema.Name)
{
    public DbSet<OrderEntity> Orders => Set<OrderEntity>();
}
```

## Register a stance the same way in every module

The write context takes the interceptors and seeding support; the read context takes neither, adds
`NoTracking`, and is the only one exposed behind an interface. Provider options — a spatial extension, a
retry policy — belong to the database, not to one module's taste: put them in one shared options extension
so two contexts over the same database cannot disagree.

```csharp
services.AddDbContext<OrderDbContext>((sp, options) =>
    options.UseOrdersDb(configuration)
        .AddInterceptors(
            sp.GetRequiredService<AuditInterceptor>(),
            sp.GetRequiredService<TenantInterceptor>(),
            sp.GetRequiredService<IDomainEventDispatchInterceptor>())
        .UseSeedingSupport(sp));

services.AddDbContext<OrderReadDbContext>(options =>
    options.UseOrdersDb(configuration)
        .UseQueryTrackingBehavior(QueryTrackingBehavior.NoTracking));
services.AddScoped<IOrderReadDbContext>(sp => sp.GetRequiredService<OrderReadDbContext>());
```

## Every module with a filtered context owns a stance test

The stance is an *assertion about the model*, so assert it. One test per module, naming every filtered
entity, fails the day someone adds an entity to a filtered context and forgets its filter, or gives a read
context write capability:

```csharp
Assert.IsAssignableFrom<IReadDbContext>(readContext);
Assert.False(typeof(IDbContext).IsAssignableFrom(readContext.GetType()));
Assert.Equal(QueryTrackingBehavior.NoTracking, readContext.ChangeTracker.QueryTrackingBehavior);
await Assert.ThrowsAsync<InvalidOperationException>(() => readContext.SaveChangesAsync());
Assert.All(TenantFilteredTypes, type =>
    Assert.Empty(readContext.Model.FindEntityType(type)!.GetDeclaredQueryFilters()));
Assert.All(TenantFilteredTypes, type =>
    Assert.NotEmpty(tenantContext.Model.FindEntityType(type)!.GetDeclaredQueryFilters()));
```

Building the model needs no database, so this is a unit test. Put it at the same path in every module.

## One data-access stance per query class

Mixing stances in one class is the Liskov violation — a caller cannot know which contract a given method
honours.

- **`XRepository`** — the tenant-bound context, including whichever filters that entity declares. The
  default.
- **`XReadRepository`** — read-only access through the module's tenant-independent read context. Its
  contract controls which data leaves the module.
- **`XPrivilegedRepository`** — unfiltered cross-tenant read/write on the writable privileged context. Only
  where such a write flow actually exists.
- **A domain fact that is not naturally an entity repository** may get its own purpose-named abstraction
  over the read context — `IStockAvailability` — where it is a real, independently consumed capability. Do
  not wrap a single query already owned by an aggregate repository in a one-method interface.

The injection site then documents itself: a service holding both `repository` and `readRepository` states
exactly which of its queries see what.

**A stance class only exists once the entity has more than one stance.** A single-stance entity is a plain
`XRepository` — don't pre-qualify it with no sibling to contrast against; rename it the day the second
stance is born.

## Declare filters per entity, and only where reads are tenant-private

Never auto-derive filters from the marker interface. The marker means "carries the owner id", not "is
filtered" — marked ≠ filtered is a per-entity product decision.

**Filter an entity only when its *reads* are tenant-private.** If the entity's core flow reads it *across*
tenants, leave it unfiltered and let the write-side interceptor guard the writes; filtering it fails those
cross-tenant reads closed, silently. A public listing read by anonymous visitors, or a counterparty's terms
read by the party responding to them, are unfiltered by design. Owner-private reads are filtered, with any
public browse split off to the read stance.

## Repository qualifiers name three independent dimensions

A qualifier describes the contract that differs from the service's unqualified default. It is not one
vocabulary to impose on every service:

- **Data-access stance** — `XRepository` (tenant-bound), `XReadRepository` (tenant-independent, read-only),
  `XPrivilegedRepository` (unfiltered and writable). **Name the composed contract, never the mechanism**: no
  `Unscoped`, no `CrossTenant`.
- **Mutability** — a `Repository<…>` surface permits writes; a `ReadRepository<…>` exposes queries only. An
  event-synced replica therefore uses `XReadRepository` even with no writable sibling: `Read` states a
  capability, not an audience.
- **Projection shape** — `XHeaderRepository`, `XAutocompleteRepository` describe the projection served, not
  visibility or write capability.

The dimensions are independent, and audience belongs at the API contract rather than in a persistence type
name. Keep the ordinary owned, scoped, writable repository unqualified.
