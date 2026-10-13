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
5. `this.` appears only in constructor assignments. Drop the every-field-access rule, and set the scaffold
   `.editorconfig` to `dotnet_style_qualification_for_field = false:error`.
6. The scaffold emits `.agents/skill-routes.json` (`gen_skill_routes.py --kind dotnet-service --into
   <project>`), with a test. The route table sends every test tier to the single test-naming owner. Without
   it, scaffolded repositories are born ungated, which is the root cause of the sandbox agent not loading
   the standards.
7. Tommy, 2026-10-13: every test tier's contract (unit, integration, e2e) opens with a full, generic,
   domain-neutral example test class (no product context such as VAT) that demonstrates the conventions
   by itself, without prose:
   - `Method_Scenario_ExpectedBehaviour` names;
   - constructor-built `private readonly` fields assigned with `this.`, and no `this.` inside test methods;
   - Arrange/Act/Assert separated by blank lines;
   - the tier's assertion library (Shouldly for integration);
   - `[Theory]` with the expected value last;
   - a `#region` per method under test.
   The same rule applies to every contract's snippet: the code is the explanation.
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
   Each role gets a full, generic, domain-neutral snippet obeying every other contract; the Processor's
   uses explicit `private readonly` fields assigned with `this.` in the constructor, never a
   primary-constructor capture, and the receive source is the broker SDK's own type, not an invented
   receiver role. `domain-events`' handler snippet drops `bus` for a constructor-assigned
   `integrationEventPublisher` field. Item 8's concern routing sends publisher, processor and handler code
   to `naming-collaborators` plus `domain-events`.

### C: learning defaults and snippet-led conventions (lower priority)

1. `dotnet:learning` must not default to treating Tommy as a .NET beginner, because he knows .NET well.
   Correct the default.
2. Conventions lead with code-snippet examples showing the rule, not prose, and every example obeys every
   other contract. Record this in the convention procedure, and apply it to the contracts slices A and B
   touch.

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

## Next Steps

1. Slices B and C together, as one conventions PR on `Refactor/OneTestingStyleStandard`. Tommy asked for a
   single conventions PR, and new branches or PRs are opt-in for him, so no further split. Implement,
   search-verify, build, review, PR and merge. Then notify `sandbox-dotnet-17`. Slice D (the identity fix)
   waits on the kit core-dependency release; slice E waits on azure Actions conformance.
