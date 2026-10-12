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

## B002

- **Kind:** bug
- **Observed/reported:** 2026-10-12. The shipped API preset accepts `Program` as its project name, then `dotnet build` fails with CS0437/CS0426: the generated top-level `Program` type shadows the imported `Program.Infrastructure` namespace. A name starting `Program.` shares this root collision.
- **Impact and priority:** P2; an accepted name produces an uncompilable API solution.
- **Source owner:** `tj-agents/dotnet` `.agents/dotnet/utility/scaffold` name validation.
- **State:** resolved
- **Repair link:** the scripted-scaffold goal, slice3, branch `Feature/ScaffoldComponents`.
- **Next action:** none; the component slice rejects the compiler-generated entry-point root before writes.
- **Resolution condition:** both names exit2 without output files and existing valid-name/component build gates pass.
- **Verification evidence:** parent generated the shipped `api` preset with `--name Program` in disposable temporary storage and ran `dotnet build Program.slnx --nologo --verbosity quiet`; build returned1 with both errors and no warnings.
- **Repair verification:** all13 scaffold regressions passed, including `Program` and `Program.Example` returning2 without writes and `Example.Program` remaining valid. All five real Windows component configurations restored, built and tested with zero build warnings or errors.
