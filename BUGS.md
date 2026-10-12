# Bugs

## B001

- **Kind:** bug
- **Observed/reported:** 2026-10-12 — CI run 38256944454 failed on Windows and Ubuntu in `.agents/tests/test_route_cli.py:139` because route resolution included `engineering:docs-and-debt`, which is no longer a current engineering capability. Cause confirmed: the dotnet skill-route generator emits the retired capability reference.
- **Impact and priority:** current-core route generation fails in CI; P2 because it blocks affected pull requests but has no reported production impact.
- **Source owner:** `tj-agents/dotnet` `.agents/dotnet/utility/skill-routes`.
- **State:** in-progress
- **Repair link:** `plans/route-capability-references/GOAL.md`
- **Next action:** resolve the current core capability owners, then repair the generator and its route assertions.
- **Resolution condition:** generated routes and focused route-resolution tests pass using the same current core revision as CI.
- **Verification evidence:** the reported Windows and Ubuntu CI failure and the generator's retired `engineering:docs-and-debt` emission.
