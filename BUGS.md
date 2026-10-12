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


## B003

- **Kind:** bug
- **Observed/reported:** 2026-10-12. Frozen scaffold head `1a87313b0ae5650bef89825ad501def946523741` fails the Sandbox row of the authored verifier: Functions cannot resolve the WithTracing extension with its generated package references; ApiFixture lacks the ConfigureTestServices import, uses obsolete parameterless PostgreSqlBuilder/MsSqlBuilder constructors and violates the selected ConfigureAwait rule. Fresh branch qualification also exposed repeated provider package pins in Dapper/hybrid integration composition. Diagnostics and rendered central-package entries confirm these defects.
- **Impact and priority:** P2; the accepted sandbox preset does not compile.
- **Source owner:** `tj-agents/dotnet` scaffold host/fixture templates and component contributions.
- **State:** in-progress
- **Repair link:** the scripted-scaffold goal, Slice4 `Feature/ScaffoldHosts`; bounded corrective branch `Fix/ScaffoldHostsQualification`.
- **Next action:** repair generated compiler errors and rerun fail-fast verification from the corrected exact source.
- **Resolution condition:** the full seven-configuration authored verifier passes Windows and Ubuntu at the delivered head, with focused Dapper/hybrid fixture branches compiled.
- **Verification evidence:** full Python suite passed35 against current core `0d797f568a53b73ff2e8c271c7aaf3f32f29035e`; verifier passed the first five rows then failed Sandbox. Exact diagnostic log: `dotnet-scaffold-hosts-matrix-54e894c3421a41789bf0c07ac372c89e/verify-matrix.log`.

## B004

- **Kind:** bug
- **Observed/reported:** 2026-10-12. Frozen head `1a87313b0ae5650bef89825ad501def946523741` introduces plaintext Functions `local.settings.json` containing storage/database configuration while the consumer .gitignore omits it. Cause confirmed: the new file has no corresponding ignore rule.
- **Impact and priority:** P2; configuring real local credentials then ordinary git add/publish can disclose secrets. No disclosed real credential was observed.
- **Source owner:** `tj-agents/dotnet` scaffold consumer .gitignore template.
- **State:** in-progress
- **Repair link:** Slice4 canonical review SEC3 and the existing scripted-scaffold goal/corrective branch.
- **Next action:** add a recursive basename ignore rule and a generated-output regression.
- **Resolution condition:** generated Functions local settings are ignored by default, focused regression passes and independent incremental security review verifies the corrected candidate.
- **Verification evidence:** immutable security review matched archive, patch and path identities; 132 in-memory selections preserved auth/container boundaries; sandbox render confirmed plaintext ConnectionStrings__Postgres and absent local-settings ignore rule.

B003 repair progress: the Functions tracing dependency is explicit, fixture imports/awaits and both image constructors are corrected, and provider package pins have one common owner. Fresh Sandbox passes; the existing bounded writer is qualifying SQL/JWT and Dapper/hybrid fixtures with checked subprocess results. Final seven-row Windows/Ubuntu evidence remains pending.

## B005

- **Kind:** bug
- **Observed/reported:** 2026-10-12. Fresh SQL/JWT fixture solution restores and builds with zero warnings/errors, then dotnet test --no-build emits a fixture-library testhost abort for missing BouncyCastle.Cryptography2.7.0 while returning zero. Cause confirmed: the fixture support library references xunit, whose xunit.core2.9.3 build props set IsTestProject=true, and the generated library had no explicit non-test classification. Its support-library output was therefore passed to test discovery without the actual test-project runtime setup.
- **Impact and priority:** P2; a successful process exit can conceal aborted test discovery in generated integration configurations.
- **Source owner:** `tj-agents/dotnet` scaffold integration fixture project and qualification.
- **State:** in-progress
- **Repair link:** existing scripted-scaffold goal/Slice4 corrective branch; same bounded L4 writer.
- **Next action:** inspect evaluated project properties, repair the fixture support-library classification if confirmed, and rerun fresh affected configurations with complete test-output inspection.
- **Resolution condition:** generated fixture support libraries are excluded from test discovery while actual UnitTests/IntegrationTests retain their runners; the final Windows/Ubuntu matrix has no testhost aborts.
- **Verification evidence:** checked per-command fresh SQL/JWT restore/build/test output in `dotnet-scaffold-IntegrationSqlServerRepairFinal-_y3_dht6`; test command returned0 but printed an abort. The writer caught the output discrepancy before source release. No live product scenarios were exercised.

B005 repair evidence: the authored fixture csproj now explicitly sets IsTestProject=false; actual integration test projects retain their runners. Parent inspected xunit.core2.9.3/build/xunit.core.props line10 and the complete SQL/JWT final log, which builds with zero warnings/errors and discovers only the IntegrationTests assembly without a testhost abort. Final all-platform qualification remains pending.

B003 final diagnosis: fresh package/reflection probes identify the missing OpenTelemetry namespace import, and rendered line mapping identifies the implicit async disposal await. A configured disposal scope preserves the original lazy Respawner initialization. Original forms reproduce CS1061/MA0004; corrected probes compile. Parent applied the specified disposal correction after the original writer released. Full-host/platform qualification is still required.
