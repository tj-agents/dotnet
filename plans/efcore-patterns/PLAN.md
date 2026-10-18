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

## Review repair: packaged snippet source ownership

Parent's independent review of `088e21f` found that relative EF contract paths only worked in the source
checkout. The dotnet canonical payload intentionally omits EF source; its snippet generator therefore
failed with FileNotFoundError. Repair keeps each contract in its owner: manifest entries declare `owner`,
source roots resolve to authored families or separate plugin payloads, and `--contract-root OWNER=DIRECTORY`
binds separately installed caches. A regression copies the real generated dotnet and efcore payloads to
an isolated temporary layout, checks both canonical/public generators, verifies missing-owner diagnostics,
and checks an explicit binding to a relocated EF cache. No fake authored-source path or duplicate EF tree.

Final baseline before this repair: full suite 82 tests in 119.671s, OK (2 optional core-checkout checks skipped).
Repair validation: focused snippet suite passed 9 tests in 17.502s; both the exact packaged canonical
reproduction and source generator `--check` exit 0; generated outputs current (759 files); diff hygiene
clean. Immutable repair commit follows this checkpoint; publication remains parent-held.

## User callout repair: concrete EF pattern examples

Tommy reported that the new specification/query-building skills were prose-only and left their boundaries
ambiguous. This source repair adds one coherent Order example: copied ids and concrete UTC instant in
ReadyOrdersSpecification; injected OrderQueryBuilder reads TimeProvider once and creates/applies criteria;
repository materializes with cancellation; registration keeps builder singleton and context/repository scoped.
Prose is consolidated around the examples and distinguishes reusable building logic from per-operation,
context-bound IQueryable values. `QueryBuilder` remains a house recommendation, not a universal industry name.

Every new C# block is owner-aware manifest content with a byte-identical generated compile fixture. Fixture-only
support stands in for the selected shared IPredicateSpecification contract; no new production framework.
Existing dotnet M003/M004 govern example correctness/compilation; no existing record matches the missing-example
callout. Parent owns the primary mistake record and global Core/Template authoring-policy repair; this branch
owns only the concrete EF skill examples and their qualification. No publication is authorized here.

Example repair verification:
- `python -B -m unittest discover -s .agents/tests -p test_snippets.py`: 9 tests passed in 11.231s,
  including every new EF C# block's manifest coverage and byte identity plus isolated packaged generation.
- Copied the four generated `efcore-*.Snippet.cs` files and fixture-only support into a temporary net10.0
  project referencing real `Microsoft.EntityFrameworkCore` 10.0.12 (including real DI abstractions), with
  nullable/implicit usings/code-style enforcement and warnings as errors. `dotnet build --configuration Release`
  succeeded with 0 warnings, 0 errors on SDK 10.0.302; evidence at
  `C:/Users/tommy/AppData/Local/Temp/efcore-pattern-examples-build.log`.
- `pwsh .agents/sync-generated.ps1 -Check`: 779 current files.
- Packaged canonical snippet generator `--check`: exit 0; `git diff --check` clean.

Parent owns incremental independent review and the publication hold. No global policy source or Search code
was changed by this repair.

## Changed-skill example conformity

The user requires a concrete example in every added/updated authored skill. The full candidate touched
eight additional code-free definitions, so this bounded repair adds demonstrations only to domain-design,
libraries-selected, naming, naming-collaborators, repositories, seeding and EF event-dispatch. Generic hubs
show concrete task-to-owner selection; selected libraries show a centrally versioned EF package reference;
C# examples show an ORM-independent repository, query-builder role, producer event seeding and explicit
SaveChanges-versus-Commit transaction ownership. The Dapper depth link now points to the generic repository
owner instead of the removed bare persistence name. No unrelated skill sweep or new design rule.

New C# fences enter the owner-aware snippet manifest and compilation fixtures. Shared-policy checker
qualification will cover every changed authored definition from `1d97dbe` through the final branch head.
Parent owns the Core/Template checker and publication hold; no external changes are made here.

Parent expanded the bounded conformity repair to the clean-moved `efcore:multitenancy` definition, which
also lacked an example. Its per-entity configuration references the current private-read context's tenant;
existing context-capability/base model composition retains OnModelCreating ownership, and public reads keep
a separate deliberate stance. The fixture supplies only the sample entity/context, not a new production base.

Conformity verification: the new shared Core checker was invoked with explicit working-tree paths for
all 13 changed authored definitions and exited 0. Focused snippet suite passed 9 tests in 13.052s.
All affected C# fixtures (including private-tenant configuration and explicit transaction ownership)
compiled against real EF Core.Relational 10.0.12 on net10.0 with 0 warnings/errors; retained log:
`C:/Users/tommy/AppData/Local/Temp/efcore-conformity-examples-build.log`.
Generated-output check reports 803 current files; packaged snippet generation exits 0; diff hygiene clean.
The committed full-range checker is run immediately after this local checkpoint commit.

## Contract opening repair

Restored the existing normal Template `Owns ...` opening rule in the nine changed contracts whose example
had been placed first. Existing ownership lines moved before the example; three EF contracts gained one
short ownership line. All fenced examples and the snippet manifest remain byte-identical. Focused snippet
suite: 9 passed in 13.657s; generation: 803 current outputs; normal Template opening helper: 9/9 passed.

The initial actual normal Template check found two baseline vendor-drift failures: `.agents/sync_generated.py`
and `.gitignore` differed from current Template. Both were unchanged against original base `1d97dbe`.
Read-only comparison proved the existing and canonical generators produce the same 803 paths and bytes;
Template update's dry run selected exactly those two files. Parent then approved bounded adoption through
Template's owning update utility. No manual vendor patch or generated-source copy was used.

After adoption, the actual normal Template check reports `efcore-standards conforms to Template`.
Focused snippet suite: 9 passed in 16.134s; source-layout suite: 5 passed in 1.473s; generator check:
803 current files. Namespace selection, shared-source ownership and snippet bytes are preserved.
The two-file canonical adoption is committed separately after the ownership repair; final committed-range
normal qualification follows that commit. Publication remains held by the parent.
