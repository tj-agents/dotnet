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
