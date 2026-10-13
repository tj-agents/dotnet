# Mistakes

## M001: Focused qualification was reported without proving the frozen build

- **Kind:** mistake
- **Observed/reported:** 2026-10-12. The source worker reported successful focused sandbox/fixture restore/build/test commands, and the parent repeated that report. The final frozen `1a87313` Sandbox build independently failed. The qualification gap's cause is not yet confirmed; no command-success explanation is assumed.
- **Impact and priority:** P2; an inaccurate build report could qualify an uncompilable candidate. Full independent verification caught it before readiness or merge.
- **Source owner:** this scripted-scaffold execution's source qualification and parent evidence acceptance.
- **State:** in-progress
- **Repair link:** `BUGS.md` B003 and the existing scripted-scaffold goal/Slice4 repair owner.
- **Next action:** reconcile the source worker's exact command/result sequence and qualify final source through checked fail-fast commands.
- **Resolution condition:** the command/evidence gap is explained and every required final build result is observed at the frozen delivered SHA using per-command failure checks.
- **Verification evidence:** source-worker focused-success report versus independent verifier diagnostics retained in B003; parent has corrected the report and dispatched the existing bounded writer to repair final source.

The corrective worker repeated a Sandbox pass report that complete retained output contradicted: `HostsRepairQualification/sandbox-final.log` still has Functions CS1061 and async-disposal MA0004. The worker now states its earlier verify output ended after restore and did not retain/check build output. This confirms an evidence-acceptance failure; the original per-command process history is not reconstructed. Parent repeated the partial report too early, corrected the goal, requested writer release and selected a fresh bounded diagnostic context. All future qualification must retain logs, await actual process completion, check every command and inspect test-output aborts.

## M002: A .NET slice was written in a generated sandbox repo without loading the applicable contracts

- **Kind:** mistake
- **Observed/reported:** 2026-10-13. An agent wrote a whole .NET slice in a generated sandbox repository (a Notes API, EF, a Service Bus publisher and consumer, logging, tests) without loading the applicable dotnet contracts. Breaches found: test names copied from `testing-integration`'s two-segment example; `Assert` used instead of Shouldly in integration tests; `this.` used on non-constructor field access; an integration event named `NoteCreated` without the `Event` suffix `dotnet:domain-events` requires; a direct publish alongside the write, which `domain-events` names as an anti-pattern, offered without saying so.
- **Impact and priority:** P2; a freshly scaffolded repo accepted .NET writes with none of its owning standards loaded, so every one of the breaches above shipped unreviewed against contract.
- **Source owner:** a dead `dotnet@dotnet` plugin key (core D4), so no `dotnet:*` skills loaded; no `.agents/skill-routes.json` in the generated repo, so nothing gated the `.cs` writes (this PR's item 6); the tier gate's "Applies here: dotnet:*" is advisory (core D6); and the agent did not read the contracts from source.
- **State:** open
- **Repair link:** this PR, for the scaffold route-table generation and its routing-by-concern rows, plus core D4/D6.
- **Next action:** Tommy will work through the full why later.
- **Resolution condition:** a freshly scaffolded .NET repo can't accept its first write of a concern until that concern's owning contracts are loaded.
- **Verification evidence:** the breaches above, read directly off the generated sandbox repo's diff.

## M003: The testing-e2e opening example broke its own contract

- **Kind:** mistake
- **Observed/reported:** 2026-10-13. The testing-e2e opening example written to the item-7 checklist broke testing-e2e's own fast-forward rule — its setup `Given` called `page.GotoAsync(...)`, which the contract's "Fast-forward without UI replay" rule forbids a setup `Given` from doing — and its assertion rule, reading the page once with `TextContentAsync` then asserting with Shouldly instead of an auto-retrying `Expect`.
- **Impact and priority:** P2; the contract's own opening example, meant to demonstrate every one of its rules by itself, demonstrated a violation of two of them instead.
- **Source owner:** the item-7 dispatch listed only the generic cross-tier checklist (naming, fields, AAA, assertion library, Theory, region), not the host contract's own rules; the convention procedure said an example must obey "every **other** contract", which by its wording excludes the one it sits in; and the review that followed was scoped to cross-contract rules, not the host contract.
- **State:** resolved
- **Repair link:** this PR. The example now fast-forwards from seeded fixture state with no browser call in its `Given`, drives the browser only in its `When`, and asserts with Playwright `Expect(...)` in its `Then`.
- **Next action:** none; the procedure wording and the example are both fixed.
- **Resolution condition:** the convention procedure's wording includes the host contract, and every snippet this branch touches has been checked against its own host contract's rules before merge.
- **Verification evidence:** the rewritten `testing-e2e` example and its re-check against the contract's "One behaviour, starting at the nearest already-verified state" and "Fast-forward without UI replay" sections, below in this session's report.

## M004: Shipped snippets didn't compile under the scaffold's own analyzers

- **Kind:** mistake
- **Observed/reported:** 2026-10-13. sandbox-dotnet applied PR #50 and found the scaffold template `.editorconfig` had no `dotnet_diagnostic.CA1848.severity = error` though `dotnet:logging` requires it, and the microservice-boundaries Processor snippet awaited without `.ConfigureAwait(false)` and used `await using var scope = …`, which the selected stack's Meziantou MA0004 rejects under `TreatWarningsAsErrors`. The scaffold's own code (`ApiFixture.cs`) already used `.ConfigureAwait(false)` throughout — this is the second contract example not to hold up under its own toolchain (M003 was the first).
- **Impact and priority:** P2; two shipped contract examples would fail to compile if a consumer pasted them into a real selected-stack repository.
- **Source owner:** no compile gate existed for `.agents/dotnet/contract/**/SKILL.md` csharp blocks; review read the prose rules, not the scaffold's analyzer configuration, so neither defect was caught before merge.
- **State:** resolved
- **Repair link:** this PR. CA1848 added to the scaffold template `.editorconfig`; the Processor snippet rewritten to the scaffold's `.ConfigureAwait(false)` / `await using (scope.ConfigureAwait(false))` pattern; and a snippet compile gate added under `.agents/tests/snippets/` — a compilable fixture plus a byte-identity unittest per snippet, `verify.py` scaffolds the sandbox preset after the positive configurations and builds every fixture, under `TreatWarningsAsErrors`, in the matching target project (Infrastructure for production snippets, the matching test project for test-tier snippets). A dedicated `skip` field (with a required, specific reason) marks a block the gate cannot or should not compile — a counter-example, a prose fragment, or a feature the scaffold doesn't target — rather than overloading the doc's existing `// CORRECT`/`// WRONG` comment convention, which marks intent inside a block but can't mark a whole block as non-compilable without altering its verbatim text. The gate caught and this PR also fixed several further snippets that didn't compile: a genuine `Fulfil.Fulfil` CS0542 self-naming bug in `keyed/unions`, a missing `Status` property in `domain/events`, missing `.ConfigureAwait(false)` in five further production-tier snippets (`errors/carriers`, `persistence` ×2, `proto`, `seeding`, `style`), and non-functional `ShouldBe`/`ReadAsync` placeholder calls in `testing/integration`.
- **Next action:** none; the gate runs on every future SKILL.md change.
- **Resolution condition:** `verify.py`'s snippet compile gate builds every non-skipped contract csharp block under the scaffold's own analyzers and passes.
- **Verification evidence:** `python -B .agents/tests/test_snippets.py` (byte-identity and coverage) and `verify.py`'s snippet compile gate build output, both in this session's report.
