# Canonical EF Core query patterns

Authorized scope: update generic standards requested by Tommy on 2026-10-18: per-operation specification parameter objects, injected query builders, and a dedicated `efcore` namespace for EF Core-specific guidance. No Search product writes are owned here.

Owner: branch `Refactor/EfCorePatterns`, isolated worktree `C:/Users/tommy/source/repos/Concertable/search/.worktrees/efcore-standards`, based on fetched `origin/main` `1d97dbe`.

Acceptance: specifications have concrete immutable criteria and no DI; query builders compose deferred EF queries; evaluator applies specifications; generic .NET remains ORM-independent; EF-only skills, manifests, detection, routes, scaffold selection and generated assets use `efcore`; generation and focused tests pass; reviewed standards are delivered under `.agents/delivery-authorization.json`.

One atomic delivery slice covers namespace ownership and all source/generated consumers: splitting it leaves installed skills or routes unresolved. Generated payloads account for most changed files. Product refactoring remains a separate parent-owned change.

## Research and decisions

Assessment complete; retain the existing product specification/evaluator APIs rather than add Ardalis or a new shared abstraction. Adopt the separation illustrated by [Ardalis constructor criteria](https://specification.ardalis.com/usage/create-specifications.html) and its [stateless evaluator](https://specification.ardalis.com/usage/use-specification-repository-pattern.html). Specifications are not intrinsically EF-specific; this skill governs their use in EF query pipelines, while generic predicate naming stays in dotnet.

[Microsoft query execution](https://learn.microsoft.com/en-us/ef/core/querying/how-query-works) establishes deferred LINQ composition; [DbContext lifetime](https://learn.microsoft.com/en-us/ef/core/dbcontext-configuration/) establishes scoped, non-thread-safe context ownership. `QueryBuilder` / `Build` is our descriptive house convention for the injected composition service, not a Microsoft-prescribed service interface. It avoids `IQueryProvider`, which names LINQ provider infrastructure, and `Query`, which ambiguously names a request or executable operation.

Clean move `dotnet:persistence` and `dotnet:multitenancy` to efcore. Keep seeding's production-write, canonical-state and idempotency rules generic; move only its EF persistence example to efcore:persistence. Split EF SaveChanges dispatch from generic domain events into `efcore:event-dispatch`; generic raising/handler/outbox rules retain `dotnet:domain-events`.

## Progress

- Fetched source; isolated worktree created from current remote main.
- Audited all authored dotnet skills and EF references. No installed caches edited.
- Next: implement the plugin split and canonical patterns, regenerate, validate, review and deliver.

- Added an explicit `efcore-service` route kind so Dapper/no-database consumers do not require the optional EF plugin. Generic `dotnet-service` remains ORM-independent.
- Fixed an audited guidance defect: `SavedChangesAsync` is save completion, not necessarily outer transaction commit; EF event-dispatch now names the transaction owner.

## Integration dependency

Central marketplace roster is parent-owned: add `efcore` from `tj-agents/dotnet` in
`tj-agents/marketplace/catalog.json` and regenerate both host catalogs after this producer merges.
The machine plugin-selection roster in `tj-agents/core` also needs `efcore: [dotnet]` before
`adopt_plugins.py --plugin efcore@tj-agents` accepts the new plugin. Parent has been notified; this
worktree does not edit those repositories or installed caches.

After both producers publish, consumer adoption is `python -B <machine-plugin-selection>/scripts/adopt_plugins.py
--root <consumer> --stack dotnet --plugin efcore@tj-agents --mode write`, then the same command with
`--mode check`. EF route generation is `gen_skill_routes.py --kind efcore-service --into <consumer>`.

## Validation checkpoint

- `pwsh .agents/sync-generated.ps1`: generated 759 current outputs; `-Check` passed after final prose changes.
- Route suite: 15 tests passed, with 2 existing optional checks skipped because this isolated worktree does not expose a core checkout at the helper's conventional paths.
- Snippet packaging suite: 8 tests passed. Existing compiled fixture text is unchanged; source ownership references moved with their skills.
- Scaffold suite: 54 tests passed before explicit route-kind addition. The added data-option selection test and generated-EF-route test pass; final complete suite is running.
- Source-layout suite: 5 tests passed, including generic .NET has no EF prerequisite and EF contracts have one explicit owner.
- Full-suite run exposed two stale test assumptions (moved persistence skill and no-argument route helper); both repaired and focused verification passed. No check was weakened or disabled.

Review and remote delivery remain. Parent owns independent review and dependent marketplace/core roster publication; producer should land first.
