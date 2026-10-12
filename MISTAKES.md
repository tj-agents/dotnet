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
