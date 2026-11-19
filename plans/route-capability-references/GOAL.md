# Repair stale shared skill-route capability references

## Outcome and completion

Repair the dotnet-owned generated route contract so every engineering capability resolves against current core main. Focused tests and Windows/Ubuntu CI pass; an independently reviewed bounded PR is merged. Return exact evidence here. This side workstream does not own or close the scripted scaffold goal.

## Authorization

engineering:session-guidance grants standing standards-defect diagnosis, implementation, testing, PR and merge after repository gates. This is a bounded source repair in tj-agents/dotnet. No edits to core, kit/Template, consumer repositories or machine installs. Preserve all existing unrelated active branches.

## Checkout and lane

Checkout: C:/Users/TommySeery/source/repos/tj-agents/dotnet/.worktrees/Fix-RouteCapabilityReferences
Branch: Fix/RouteCapabilityReferences
Base: origin/main bfd6c2200801ccba8ce60c684d0f9662d5a3f3fe
PR: https://github.com/tj-agents/dotnet/pull/44
L4: a small testable compatibility fix; the concrete failure identifies retired engineering:docs-and-debt references. Resolve correct current narrow owners from current core source evidence before substituting; do not weaken route resolution tests.

## Evidence and scope

Dotnet CI run 38256944454 for unrelated PR41 fails on both Windows and Ubuntu in .agents/tests/test_route_cli.py:139: AssertionError for engineering:docs-and-debt. .agents/dotnet/utility/skill-routes/scripts/gen_skill_routes.py lines50-51 emit it for agent instructions and TECH_DEBT.md. Local tests pass against older nearby core; hosted CI fetches current core main. Existing worktree/PR inventory found no distinct route-repair owner. This is independent of scaffold generation; original owner continues that goal.

Own only .agents/dotnet/utility/skill-routes source and directly affected tests, generated projections, BUGS.md and this goal. One small standalone slice. Do not alter vendored CI/generator, scaffold/structure files or other plans. Verify against current core revision in task-temporary read-only materialization if local primary core is stale. Follow exact-head review and repository delivery authority; never bypass failing checks.

## Next Steps

1. Acknowledge pickup here before edits; read repository instructions, lanes, bugfix and problem-record conventions. Record B001 in root BUGS.md with concrete failure, source owner, repair goal and resolution condition.
2. Inspect current core skill identities, repair only retired route references and expected assertions; preserve meaningful route-resolution tests. Regenerate and run exact generator/pinned kit checks and focused tests using the same current core revision CI sees.
3. Commit, independently review, open bounded draft PR and monitor Windows/Ubuntu exact-head checks. Resolve findings and CI failures, merge when gates pass, then record PR/merge SHA and notify originating owner through this saved goal.
4. Leave original scaffold owner active. No duplicate successor, no settings rollout, no core modifications. Original owner will reconcile this source repair after merge.

## Progress

- 2026-10-12 — Picked up from `C:\Users\TommySeery\source\repos\tj-agents\dotnet\.worktrees\Feature-ScriptedScaffold\plans\scripted-scaffold\route-repair-handoff.md` in the recorded `Fix/RouteCapabilityReferences` checkout. Read repository instructions, lane, plan-execution, bugfix, and problem-record conventions; selected L4 for the specified, focused route repair. Recorded `B001` in root `BUGS.md`.
- 2026-10-12 — Verified current core `ccd97bb88f79a885d9d77fa43faaa7dd6abebb72`: its compatibility map resolves the retired alias to `engineering:docs`, and its `write-debt` convention owns `TECH_DEBT.md`. Replaced the instruction-file route with `engineering:docs` and the debt-file route with `engineering:write-debt`; regenerated projections. Passed `python -B -m unittest discover -s .agents/tests -p "test_*.py"` (16 tests) against that core checkout and `pwsh -NoProfile -File .agents/sync-generated.ps1 -Check` (144 generated outputs current).
- 2026-10-12 — PR #44 at `7b25dede44a4f84c384726a5538ef31fc0ab17ef` passed hosts, Ubuntu, and Windows CI; native review returned no actionable findings. It merged as `49cabb0eb4b6723f20f2bb0bbb82bfb4fcec59df`. `B001` is resolved. This record notifies the originating scripted-scaffold owner; its goal remains active and this side workstream made no scaffold, core, consumer, or machine-install changes.

```completion
{
  "outcome": "Generated .NET service routes resolve current engineering capabilities.",
  "acceptance": [
    {
      "id": "route-capability-resolution",
      "criterion": "Focused tests and Windows/Ubuntu CI pass for the repaired route references.",
      "evidence": [
        {"source": "local validation", "result": "16 focused repository tests and generated-file drift check passed against core ccd97bb88f79a885d9d77fa43faaa7dd6abebb72."},
        {"source": "PR #44", "result": "hosts, Ubuntu, and Windows checks passed before merge commit 49cabb0eb4b6723f20f2bb0bbb82bfb4fcec59df."}
      ],
      "owner": "route-capability-references side-workstream",
      "next_action": "None; resolved."
    }
  ],
  "deliveries": [
    {"repository": "tj-agents/dotnet", "pr": 44, "head": "7b25dede44a4f84c384726a5538ef31fc0ab17ef"}
  ],
  "open_tasks": []
}
```
