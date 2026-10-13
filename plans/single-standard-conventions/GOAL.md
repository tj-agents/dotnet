# One standard for the dotnet conventions

Status: in progress (2026-10-13). Decided by Tommy on 2026-10-13 and relayed by the sandbox-dotnet session
from `tomjseery/sandbox-dotnet` wiring evidence. Owner: the Claude session that delivered the azure
app-profile goal (`tj-agents/azure` `plans/app-profile/GOAL.md`, complete).

## Rule for every slice

Leave exactly one standard. Remove every superseded name, example and rule across contracts, scaffold
components, templates, presets, tests, docs and generated plugin copies. Add no compatibility alias and no
second vocabulary. Prove it with a repository-wide search before each PR. Record each contract change with
its one-line why and the date, under `dotnet:learning`'s convention procedure.

## Slices (one PR each, delivered in order)

### A: single-service layers (`Refactor/SingleServiceLayers`)

1. `dotnet:structure-single-service` replaces `<Name>.Core` with:
   - `<Name>.Domain`: entities, value objects and domain events;
   - `<Name>.Application`: services, repository interfaces, DTOs and requests, mappers.

   It keeps `<Name>.Infrastructure` and renames the host `<Name>.Api` to `<Name>.Web`. Why: one vocabulary
   with `dotnet:structure-modules`, where Domain already means entities only and Application holds services
   and DTOs.
2. Host naming rule, stated in both structure contracts: "Api" is a module's endpoint layer (as
   `structure-modules`' `X.Api`); "Web" is the process host that serves the whole web API.
3. Carry it through the scaffold:
   - components, templates, presets, `verify.py` and tests;
   - the cloud=azure profile's build commands and project paths (`src/<N>.Web`, and the migration bundle's
     `--startup-project`).
4. A repository-wide search finds no `<Name>.Core`, `$NAME$.Core` or single-service Api-host references.

### B: testing and style, one standard each

1. Test naming has one owner and one rule for every tier, and every example conforms. Today
   `testing-unit` has `Method_Scenario_ExpectedBehaviour`, `naming` routes only unit-test naming there, and
   `testing-integration`'s examples use two segments.
2. The per-tier assertion library has one owner, and the examples obey it. Today `testing-integration`'s
   example mixes `Assert.*` with `ShouldBe`.
3. The scaffold's IntegrationTests project references Shouldly, and the per-tier library is build-gated as
   the contract says.
4. The `testing-integration` example uses explicit `private readonly` fields, not a primary-constructor
   fixture capture, per `dotnet:style`.
5. Tommy, 2026-10-13 (Option A): `this.` appears only where a constructor parameter shadows the field or
   property it fills. Drop the every-field-access rule, set the scaffold `.editorconfig` to
   `dotnet_style_qualification_for_field = false:error`, and add `EnforceCodeStyleInBuild` so the setting
   actually runs at build time. Verified during implementation: this only gates the "add missing `this.`"
   direction (IDE0009) — IDE0003 ("remove this.") does not fire as a build diagnostic in this SDK under
   any configuration tried, so a stray `this.` outside a constructor is still caught by review and example,
   not by `dotnet build`.
6. The scaffold emits `.agents/skill-routes.json` (`gen_skill_routes.py --kind dotnet-service --into
   <project>`), with a test. The route table sends every test tier to the single test-naming owner. Without
   it, scaffolded repositories are born ungated, which is the root cause of the sandbox agent not loading
   the standards.
7. Tommy, 2026-10-13: every test tier's contract (unit, integration, e2e) opens with a full, generic,
   domain-neutral example test class (no product context such as VAT) that demonstrates the conventions
   by itself, without prose:
   - `Method_Scenario_ExpectedBehaviour` names;
   - constructor-built `private readonly` fields, `this.` only where a constructor parameter shadows one
     (Option A, item 5), and no `this.` inside test methods;
   - Arrange/Act/Assert separated by blank lines;
   - the tier's assertion library (xUnit for unit, Shouldly for integration, Playwright `Expect` for e2e
     page state and Shouldly for a value read outside the page);
   - `[Theory]` with the expected value last;
   - a `#region` per method under test.
   The same rule applies to every contract's snippet: the code is the explanation, and it must obey every
   contract that applies to it, including the one it sits in (M003: an earlier e2e example broke its own
   contract's fast-forward and assertion rules).
8. Tommy, 2026-10-13: record M002 in `MISTAKES.md`: a sandbox .NET slice was written without loading the
   dotnet contracts. Item 6's route table must route by concern as well as by path (events,
   publishers/consumers, logging, validation, errors, DI, endpoints, persistence, collaborators), so every
   applicable contract is required before the write.
9. Tommy, 2026-10-13 (relayed by sandbox-dotnet-17, proposal at
   `C:\Users\TommySeery\.claude\plans\tj-agents\DOTNET_MESSAGING_ROLES_PROPOSAL.md`): `dotnet:naming-collaborators`
   gains two canonical roles — publishing an integration event (`IIntegrationEventPublisher`, one per
   solution, generic over the event) and pumping a broker subscription (`<Subscription>Processor :
   BackgroundService`, dispatching to the existing Handler role and settling the message) — because the
   sandbox invented `INoteEventPublisher` and a `HostedService` for exactly these with no role to reuse.
   Each role gets a full, generic, domain-neutral snippet obeying every contract that applies to it; the Processor's
   uses explicit `private readonly` fields assigned with `this.` in the constructor, never a
   primary-constructor capture, and the receive source is the broker SDK's own type, not an invented
   receiver role. `domain-events`' handler snippet drops `bus` for a constructor-assigned
   `integrationEventPublisher` field. Item 8's concern routing sends publisher, processor and handler code
   to `naming-collaborators` plus `domain-events`.
10. Tommy, 2026-10-13: `dotnet:libraries-selected`'s table lists xUnit, Reqnroll and Playwright but no
    assertion library, so it gains an Assertions row pointing to `dotnet:testing` — the one owner for
    which library each tier uses — so no agent is ever asked this again.
11. Negative-path scaffold gates: `verify.py` scaffolds one IntegrationTests configuration and asserts
    `dotnet build` FAILS for a stray `Assert.*` in an integration test (`BannedApiAnalyzers`/RS0030),
    restoring the file after. It also injects a stray `this.field` read outside a constructor and reports
    the result either way: in the current SDK this one does not fail the build (see item 5's finding), so
    it prints the finding rather than failing `verify.py` on a gate the toolchain doesn't support yet.

### C: learning defaults and snippet-led conventions (lower priority)

1. `dotnet:learning` must not default to treating Tommy as a .NET beginner, because he knows .NET well.
   Correct the default.
2. Conventions lead with code-snippet examples showing the rule, not prose, and every example obeys every
   contract that applies to it, including the one it sits in. Record this in the convention procedure, and
   apply it to the contracts slices A and B touch.

### D: packaging identity and the core dependency (Tommy, 2026-10-13)

1. `plugins/dotnet/harness.json` and its source declare the plugin as `dotagents/dotnet` and require
   marketplace id `dotagents`. Make it `tj-agents` everywhere, and verify with a repository-wide search
   that no `dotagents` remnant is left.
2. "dotnet inherits core": `selection.json` has `"dependencies": []`, and the marketplace entry declares
   none. Tommy widened this on 2026-10-13: it is systemic across every stack, and the kit/Template must
   make a stack inherit core by default, with `kit:check` enforcing it. kit has its own live owner (the
   Codex Template goal), so the requirement is written at
   `C:\Users\TommySeery\.claude\plans\tj-agents\TEMPLATE_STACK_INHERITS_CORE.md` for Tommy to give it.
   dotnet then picks the dependency up via `kit:update` and doesn't hand-declare it. Waits on that kit
   release.
3. The README gives a one-step install and use.
4. Before changing the published identity, check what installed consumers of the legacy `dotagents`
   marketplace rely on. The marketplace README says legacy marketplaces stay available, and core owns
   release identities. If the change would break published installs or needs a core release-catalog
   change, ask Tommy one line before merging.

### E: hand workflows to the deploy-target owner (after azure `Feature/ActionsConformance` merges)

With `cloud=azure`, the dotnet scaffold writes its restore, build and test commands into the profile's
`verify` list and stops emitting `.github/workflows/ci.yml`. azure then owns the workflow tree, per
`github-actions:structure`. Goal: tj-agents/azure `plans/actions-conformance/GOAL.md`.
It also writes `database.schemas` into the profile from the EF model's schemas (the scaffold's default
schema, or a `cloud-db-schemas` option), so the workload grants cover them.

## Lanes

- Each slice is specified implementation at L4, run by one in-session lane agent as the only writer.
  Tommy's limit is 7 sessions on this machine, so no extra CLI sessions.
- Review is an independent lens per PR.

## Progress

- 2026-10-13: goal created on `Refactor/SingleServiceLayers` from main `a5b8a07` (after PR #48).
- 2026-10-13: slice A was implemented in `c12e6f8`.
  - The contracts (single-service, plus the host-naming rule in both structure contracts) and the scaffold
    use Domain/Application/Web. The `hosts` value `api` became `web`, and so did the azure workload id.
  - The searches find only the dated decision bullet.
  - 42 unittests, sync and kit check pass, and all 8 verify.py configurations build and test, including
    SandboxAzure with Terraform validate.
  - Parent correction sent: rename the component folders and the `API_*` placeholders that still mean the
    Web host. `ApiFixture` and the testing vocabulary are left for slice B.
- 2026-10-13: `59308cd` renamed the component folders (`web`, `azure-web`, `azure-web-postgres`,
  `azure-telemetry-web`) and `API_*` to `WEB_*`. The searches are clean, and 42 tests plus the SandboxAzure
  verify pass.
  - `test_route_cli.py`'s `engineering:docs` failure reproduces on main `a5b8a07`, so it's pre-existing and
    unrelated.
  - Next: rename the `api` preset and the `Api*Sample` verify names to Web.

- 2026-10-13: **slice A merged** as tj-agents/dotnet#49 → `b5e395c`.
  - It covers `59308cd` (component and placeholder renames) and `93eb064` (the preset and samples).
  - The review approved with no findings, and CI was green, including the azure end-to-end run.
  - sandbox-dotnet was notified.
- 2026-10-13: slice B started on `Refactor/OneTestingStyleStandard` from `b5e395c`.
- 2026-10-13: B9 added — `naming-collaborators` gained the Publisher and Processor roles, `domain-events`'
  handler snippet now injects `IIntegrationEventPublisher`, and the route table sends publisher/processor/
  handler code to `naming-collaborators` and `domain-events`.
- 2026-10-13: **slices B and C implemented** in `985fb68`, including B9. The repo-wide searches are clean
  (no second test-naming rule, no two-segment names, no `Assert.*` in the integration example, no `this.`
  outside a constructor in any example or template), `test_scaffold.py`/`test_route_cli.py`/
  `test_source_layout.py` pass (the `engineering:docs` failure in `test_route_cli.py` is the same
  pre-existing one reported on main), `sync-generated.ps1 -Check` and `kit:check` pass, and all 8
  verify.py configurations build and test, including SandboxAzureSample with Terraform validate.
  Not yet reviewed, PR'd or pushed.
- 2026-10-13: PR #50 opened from `985fb68`/`22bc92b`; three follow-up commits landed directly on the PR
  branch (`af2e298` real-SDK Processor dispatch, `3d8276d` the publisher/handler-vs-processor routing
  split, `b65312d` recording the two decisions below as pending), then the two decisions were made and
  implemented:
  - **`this.` versus the build gate (items B5/B7):** Option A — `this.` only where a constructor parameter
    shadows the field or property it fills. Every non-shadowed `this.` across the contracts and scaffold
    is fixed (`testing-unit`'s `InventoryTests`, `ApiFixture`'s `container`, two `DapperConnectionFactory`
    variants' `connectionString`, `dependency-injection`'s `Reserve`/`Charge`/`Dispatch`), and the scaffold's
    `Directory.Build.props` gains `EnforceCodeStyleInBuild` so `false:error` actually runs at build time.
  - **E2E assertions (item 10):** both, split by what's being asserted — Playwright `Expect(locator)` for
    page state, Shouldly for a value read outside the page. `dotnet:testing`'s table and `testing-e2e`'s
    example both record it, and `dotnet:libraries-selected` gains the Assertions row pointing to
    `dotnet:testing` so the split is never re-asked.
  - M003 recorded in `MISTAKES.md`: the first E2E rewrite broke its own contract's fast-forward and
    assertion rules, because the checklist and the convention procedure both said "every **other**
    contract". The example is rewritten to fast-forward from seeded fixture state with no browser call in
    its `Given`, and the procedure wording now says "every contract that applies to it, including the one
    it sits in".
  - Negative-path scaffold gates (item 11) added to `verify.py`.
  - M003 and item 6's own checklist exposed the same gap a layer up: re-checking every snippet this branch
    touches against its own host contract found testing-e2e's rewrite needed the fast-forward/assertion fix
    above; unit, integration, naming-collaborators, domain-events, microservice-boundaries and style were
    already each consistent with their own rules.
  - Finding, not fixed: IDE0003 ("remove this qualification") does not fire as a build diagnostic in the
    SDK in use, verified by isolated repro across field/property/method access, `dotnet_diagnostic.IDE0003.severity`,
    `dotnet format`, and with `Meziantou.Analyzer` added — only IDE0009 ("add this qualification") fires.
    `verify.py`'s negative-path gate for a stray `this.field` outside a constructor therefore reports this
    rather than asserting a build failure that the toolchain doesn't produce; "this. only where shadowed"
    is enforced by review/example today for that direction, not by the build. Left for Tommy to decide an
    alternative mechanism, or to accept it as a review-only rule.
  - Repo-wide searches re-run clean: no non-shadowed `this.` anywhere in `.agents/dotnet`, no
    `TextContentAsync`-then-`ShouldBe` left in the e2e example. `test_scaffold.py`/`test_route_cli.py`
    (same pre-existing `engineering:docs` failure)/`test_source_layout.py`, `sync-generated.ps1 -Check` and
    `kit:check` pass, and all 8 verify.py configurations plus the new negative-path gates ran sequentially
    and passed (0 warnings/0 errors on every config, both Terraform roots validated).
- 2026-10-13: slice B/C **PR #50 merged** as `4cb90a2`.

- 2026-10-13: **Follow-up fixes** — `Fix/SnippetsCompileUnderScaffold`, from sandbox-dotnet applying #50
  and finding two defects the review missed: the scaffold template `.editorconfig` had no
  `dotnet_diagnostic.CA1848.severity = error` though `dotnet:logging` requires it, and the
  microservice-boundaries Processor snippet awaited without `.ConfigureAwait(false)` and used
  `await using var scope = …`, which the selected stack's Meziantou MA0004 rejects under
  `TreatWarningsAsErrors` (M004 in `MISTAKES.md`).
  - Fixed both instances, then built a snippet compile gate so the class of defect can't recur: a
    compilable fixture plus a byte-identity unittest per `.agents/dotnet/contract/**/SKILL.md` csharp
    block, under `.agents/tests/snippets/`. `verify.py` scaffolds the sandbox preset after the positive
    configurations, adds a temporary Dunet reference for the Infrastructure project's union snippets, copies
    each fixture into its target project (Infrastructure for production snippets, the matching test project
    for test-tier snippets), and builds under `TreatWarningsAsErrors`.
  - A block that is a deliberate counter-example or otherwise can't compile (a prose fragment, a
    net11.0-only feature, a scope-colliding multi-example fence) gets a dedicated `skip` field with a
    required, specific reason — a new explicit marker, not the doc's existing `// CORRECT`/`// WRONG`
    comments, since those mark intent inside a block rather than exempting a whole block from the gate
    without touching its verbatim text.
  - The gate found and this PR fixed further genuine snippet defects beyond the two reported: a
    `Fulfil.Fulfil` CS0542 self-naming bug in `keyed/unions` (the union must be named `Fulfilment`), a
    missing `Status` property in `domain/events`, missing `.ConfigureAwait(false)` in five further
    production-tier snippets (`errors/carriers`, `persistence` ×2, `proto`, `seeding`, `style`), and
    non-functional `ShouldBe`/`ReadAsync` placeholder calls in `testing/integration` replaced with real
    Shouldly/`System.Net.Http.Json` calls.
  - 6 new unittests, sync and kit check pass, and the full verify.py (including the new snippet compile
    gate) runs sequentially and passes.

## Next Steps

1. Slices B and C merge as one conventions PR, tj-agents/dotnet#50. Then notify `sandbox-dotnet-17` for
   the B9 renames.
2. Pending Tommy: enforce "no stray `this.`" with a scaffold-shipped source-scan test, or keep it
   review-only. The scan test would parse the solution's `.cs` files with
   `Microsoft.CodeAnalysis.CSharp` syntax and fail on a `this.` that isn't a constructor assignment
   shadowed by its parameter. IDE0003 can't gate it on SDK 10.0.301.
3. Slice E, once azure `Feature/ActionsConformance` (tj-agents/azure#5) merges.
4. Slice D waits on the kit core-dependency release.
