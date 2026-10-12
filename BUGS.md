# Bugs

## B001

- **Kind:** bug
- **Observed/reported:** 2026-10-12 — CI run 38256944454 failed on Windows and Ubuntu in `.agents/tests/test_route_cli.py:139` because route resolution included `engineering:docs-and-debt`, which is no longer a current engineering capability. Cause confirmed: the dotnet skill-route generator emits the retired capability reference.
- **Impact and priority:** current-core route generation fails in CI; P2 because it blocks affected pull requests but has no reported production impact.
- **Source owner:** `tj-agents/dotnet` `.agents/dotnet/utility/skill-routes`.
- **State:** resolved
- **Repair link:** `plans/route-capability-references/GOAL.md` and PR #44
- **Next action:** none; resolved.
- **Resolution condition:** generated routes and focused route-resolution tests pass using the same current core revision as CI.
- **Verification evidence:** `python -B -m unittest discover -s .agents/tests -p "test_*.py"` passed 16 tests against core `8e7110da37540971be623eabd847618ee32ea04c`; generated outputs were current; and PR #44 passed hosts, Ubuntu, and Windows CI before merging as `bd524c3564895e41a79d3ea2605e63eb7173a1a6`.
