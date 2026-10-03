---
name: naming-repositories
description: Canonical C# repository contracts independent of an ORM — read, write and combined capabilities; entity and visibility qualifiers; query and write verbs; nullable single-row results, collections and predicates; and the boundary to application resolvers and result carriers. Use when naming or reviewing a repository, persistence method, or extracted application collaborator.
kind: contract
domain: dotnet
profile: core
applicability: C# projects exposing repository contracts, regardless of persistence library
requires: none
provenance: house
---

# Repository naming and contracts

Owns repository capability names, query/write verbs, storage return shapes and the application boundary.

## Applicability and ownership

These house conventions apply wherever a project exposes repositories. Shared identifiers follow
`dotnet:naming`. EF Core mechanics and the selected repository base
hierarchy belong to `dotnet:persistence` when that profile applies. A project
can use this naming contract without choosing EF Core, tenancy, a result library or a dispatch architecture.

## Name the entity and exposed capability

| Exposed capability | Interface and implementation |
|---|---|
| Read-only persistence operations | `IOrderReadRepository` / `OrderReadRepository` |
| Write-only persistence operations | `IOrderWriteRepository` / `OrderWriteRepository` |
| Combined read and write operations | `IOrderRepository` / `OrderRepository` |

Use the established entity or read-model subject. A narrower interface can be implemented by its
existing repository when that repository owns the capability. The interface's operations determine
its capability, including when a query enlists a writable context in an existing transaction.
Transaction participation and use by an authorization operation preserve that persistence role.

Visibility is a separate qualifier. When the project selects multitenancy, compose its
visibility convention in `dotnet:multitenancy` with the exposed capability, such as
`OrderPrivilegedReadRepository`. Framework-owned repository interfaces keep their framework contracts.

## Query and write contracts

| Operation | Name form | Returned contract |
|---|---|---|
| Retrieve one persisted row or projection | `GetByIdAsync`, `GetDetailsByCustomerIdAsync` | The value or `null` when no row matches |
| Retrieve zero or more values | `GetByCustomerIdAsync`, qualified by the returned shape when needed | A read-only collection; no matches is empty |
| Retrieve unique values | `GetExistingIdsAsync` | A read-only set |
| Test existence | `ExistsByCustomerIdAsync` | `bool` |
| Aggregate persisted values | `GetUnreadCountByCustomerIdAsync` | The declared count or aggregate value |
| Stage or perform a write | The selected persistence API's `Add`, `Insert`, `Update`, `Remove` or explicit operation verb | Its staging/completion or affected-row contract |

Select distinguishing names from the actual parameters and output. Where a single-row and collection
query would otherwise have identical names and parameters, expose their shape or cardinality clearly.
Every asynchronous operation uses `Async`, accepts cancellation when it can reach I/O and propagates it.

Expose locking guarantees callers must rely on, such as `GetByIdForUpdateAsync` or
`GetSnapshotsByIdsForShareAsync`. A composite identity can use an established domain key as a whole:
`receipts.GetByRequestForUpdateAsync(tenantId, operation, requestId, ct)`. Preserve every identity
predicate; spell out component names when they distinguish different queries.

## Persistence and application boundaries

Repositories own storage queries, filtering, projection, persistence and the locks/enlistment supporting
those operations. Returned payload names follow
`dotnet:naming-data-contracts`; a final `OrderSummary` retains that name
when a repository projects it directly.

Application selection, resolution rules and the interpretation of several persisted inputs belong to
the appropriate collaborator under `dotnet:naming-collaborators`.
That collaborator consumes repository queries and exposes its own operation and returned outcomes.
A project location named Infrastructure can contain implementations on both sides of this boundary.

Repository single-row absence remains nullable. The consuming application boundary converts that
absence according to its contract: ordinary presence/absence, a named rejection or a guaranteed value.
Projects selecting Reunion use `dotnet:errors-carriers` for that conversion.
Extracting an operation into an application collaborator includes its return contract and caller
handling as well as its implementation, registration and name. Preserve locking, cancellation and
scope guarantees while separating the owners.
