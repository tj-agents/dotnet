# Multitenancy

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
- **`AdminDbContext`** (abstract) — the platform-admin stance: no tenancy, but **writable**, so a
  cross-tenant operator can act on rows it does not own. The interceptor's write guard no-ops for a
  tenant-less admin.

## One data-access stance per query class

Mixing stances in one class is the Liskov violation — a caller cannot know which contract a given method
honours.

- **`XRepository`** — the tenant-bound context, including whichever filters that entity declares. The
  default.
- **`XReadRepository`** — read-only access through the module's tenant-independent read context. Its
  contract controls which data leaves the module.
- **`XAdminRepository`** — privileged cross-tenant read/write on the writable admin context. Only where an
  admin write flow actually exists.
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
  `XAdminRepository` (unfiltered and writable). **Name the composed contract, never the mechanism**: no
  `Unscoped`, no `CrossTenant`.
- **Mutability** — a `Repository<…>` surface permits writes; a `ReadRepository<…>` exposes queries only. An
  event-synced replica therefore uses `XReadRepository` even with no writable sibling: `Read` states a
  capability, not an audience.
- **Projection shape** — `XHeaderRepository`, `XAutocompleteRepository` describe the projection served, not
  visibility or write capability.

The dimensions are independent, and audience belongs at the API contract rather than in a persistence type
name. Keep the ordinary owned, scoped, writable repository unqualified.
