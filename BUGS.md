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
- **State:** resolved
- **Repair link:** Slice4 canonical review SEC3 and the existing scripted-scaffold goal/corrective branch.
- **Next action:** none; corrected default ignore and generated-output regression are independently verified.
- **Resolution condition:** generated Functions local settings are ignored by default, focused regression passes and independent incremental security review verifies the corrected candidate.
- **Verification evidence:** immutable security review matched archive, patch and path identities; 132 in-memory selections preserved auth/container boundaries; sandbox render confirmed plaintext ConnectionStrings__Postgres and absent local-settings ignore rule.

B004 resolution evidence: at d573967, independent L2 security verified generated Git check-ignore matches .gitignore:5:local.settings.json, the focused regression and complete36-test suite passed, and Azure.Functions.Sdk1.0.1 marks the local settings CopyToPublishDirectory=Never. No real credential disclosure was observed.

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

## B006

- **Kind:** bug
- **Observed/reported:** 2026-10-12. The inherited consumer CLAUDE.md template contains a title and prose redirect, while the governing paired-instruction contract requires exactly @AGENTS.md. Cause confirmed: the legacy template predates the final paired-content assertion.
- **Impact and priority:** P3; generated consumer instruction files drift from the shared host contract.
- **Source owner:** `tj-agents/dotnet` scaffold consumer CLAUDE.md template.
- **State:** resolved
- **Repair link:** the scripted-scaffold goal/Slice4 final candidate.
- **Next action:** none; consumer pointer is corrected and generated host projections are regenerated.
- **Resolution condition:** root and consumer-template CLAUDE.md files have their AGENTS.md sibling and exact pointer content; generator/parity checks pass.
- **Verification evidence:** frozen081e831 assertion identified the consumer template while the repository root pair was correct. Parent replaced the authored consumer content with @AGENTS.md and checks both directions/content alongside the exact wrapper and generated parity.


## B007

- **Kind:** bug
- **Observed/reported:** 2026-10-12. Independent exact-version Testcontainers4.16.0 assembly inspection confirms that generated bare integration builders use known PostgreSQL/SQL Server administrator passwords and publish random ports without HostIP, exposing them on Docker's default interfaces. Cause confirmed: generated builders omit credential and binding overrides.
- **Impact and priority:** P2; a network-reachable running temporary test database permits unauthorized administrator access, test-data disclosure/tampering or disruption. No production database or host compromise was demonstrated.
- **Source owner:** tj-agents/dotnet scaffold integration database components/fixture.
- **State:** in-progress
- **Repair link:** scripted-scaffold Slice4 PR47 and canonical review SEC4.
- **Next action:** generate cryptographically random fixture credentials and local loopback bindings; compile both providers and independently review the corrected candidate.
- **Resolution condition:** generated PostgreSQL/SQL Server fixtures use fresh strong credentials and explicit loopback publication; regressions and real builds pass, and independent security verifies the corrected exact source.
- **Verification evidence:** frozen d573967 security lens inspected exact installed assemblies, default credentials and HostPort-only conversion; network exploitability requires a started fixture and reachability. No live containers were started.

B007 corrective evidence: the released four-file manifest3aa364769bc8c17a0381bb99c3a8ac3836c3a8d85732401852185d4c985f1209 matches parent source byte-for-byte after decoding its UTF8 BOM. All20 focused and36 current-core c91b60c9 repository tests pass. Both Dapper/PostgreSQL and hybrid/SQL Server build logs have zero warnings/errors and actual exit0; both offline binding tests pass without starting containers. Exact4.16 IL shows same-key port merge overwrites defaults, the converter emits one qualified binding, and parameter modifiers run after HostConfig conversion. Per-fixture24-byte CSPRNG passwords satisfy SQL complexity and127.0.0.1 limits publication. Final immutable independent review/platform qualification remain pending.

## B008

- **Kind:** bug
- **Observed/reported:** 2026-10-13. The .NET-to-Azure scaffold writes two competing CI workflows. Real `new --preset minimal --set cloud=azure --azure-scaffold <Azure script>` produced the .NET project, then Azure failed with `already exists: .github/workflows/ci.yml`. Cause confirmed: .NET writes that file and the default Azure workflows=true plan also owns it; the isolated Azure dry-run uses an empty directory and misses this integration collision.
- **Impact and priority:** P2; default chained cloud scaffolding fails after partial project creation. Repository standards injection succeeded before this independent component failure.
- **Source owner:** tj-agents/dotnet scaffold Azure invocation/preflight; Azure owns its workflow generator.
- **State:** in-progress
- **Repair link:** `plans/single-standard-conventions/GOAL.md`, branch `Fix/SnippetsCompileUnderScaffold`, and the CI repair boundary in `reviews/Fix-SnippetsCompileUnderScaffold.md`; first observed during the docs standards-injection acceptance goal.
- **Next action:** qualify the repaired exact head through full Linux/Windows Scaffold CI, then complete independent incremental review and delivery.
- **Resolution condition:** real default .NET cloud=azure scaffolding with the released Azure command completes, emits one intended CI workflow and passes an integration regression; collision failures occur before project publication.
- **Verification evidence:** native disposable proof at C:/Users/TOMMYS~1/AppData/Local/Temp/never-again-real-snapshots-b3il2268/StandardsProof reproduces the failure. The separate supported azure.workflows=false case at StandardsTerraformProof completes with 46 files, required standards lock/catalog and both host settings, and real Azure Terraform files. That option qualifies this injection test, not a repair of the default workflow collision.
- **Repair verification (2026-10-13):** full Scaffold run `38433756313` reproduced the collision on Linux and Windows at `9559be3`. The dotnet plan now omits its placeholder `ci.yml` for existing `cloud=azure` selections before writing any file. The fake-provider regression rejects an occupied path and writes its own CI. All 43 scaffold tests pass; a real primary Azure scaffold composition of `SandboxAzureInterop` completes and emits the six Azure-owned workflows, including `ci-complete`. No dotnet or Terraform process ran locally. Full exact-head CI and delivery remain pending.

## B009

- **Kind:** bug
- **Observed/reported:** 2026-10-13. Independent frozen review of `9559be3` found that `verify.py` resolves snippet assets only from the authored layout. Generated Claude/Codex hosts and the packaged scaffold resolve nonexistent fixture paths. Cause confirmed: the canonical assets lived outside the scaffold skill and were not shipped with its newly permitted verification command.
- **Impact and priority:** P2; the supported packaged verification command fails before contract snippet compilation.
- **Source owner:** `tj-agents/dotnet` scaffold verification script and snippet assets.
- **State:** resolved
- **Repair link:** `plans/single-standard-conventions/GOAL.md`, branch `Fix/SnippetsCompileUnderScaffold`, and `reviews/Fix-SnippetsCompileUnderScaffold.md` finding SSN-1.
- **Next action:** parent completes independent incremental review, full exact-head CI and delivery.
- **Resolution condition:** one canonical asset directory is shipped beside every verifier; authored, Claude, Codex and packaged paths resolve complete, byte-identical fixtures and pass per-fence identity plus scaffold-setup smoke checks.
- **Verification evidence:** all assets moved under `.agents/dotnet/utility/scaffold/snippets`, with no old canonical directory. The verifier uses `ROOT / "snippets"`; its authoring generator resolves the source contract owner. Eight snippet tests pass, including all three actual generated host inventories and four real scaffold-setup runs with dotnet calls mocked. All 585 generated outputs are current; kit 1.2.1, source layout and tier/harness checks pass. Runtime C# compilation and delivery remain pending.

## B010

- **Kind:** bug
- **Observed/reported:** 2026-10-13. Independent frozen review of `9559be3` found that `keyed-strategies-04-call-site` is skipped as having no named types, although its source block fully declares `Fulfilment` and `CourierFulfilment` with no missing dependencies. Cause confirmed: an inaccurate manifest exemption hides a compilable contract fence.
- **Impact and priority:** P2; the compile gate omits a complete contract example it promises to cover.
- **Source owner:** `tj-agents/dotnet` scaffold snippet manifest.
- **State:** resolved
- **Repair link:** `plans/single-standard-conventions/GOAL.md`, branch `Fix/SnippetsCompileUnderScaffold`, and `reviews/Fix-SnippetsCompileUnderScaffold.md` finding SSN-2.
- **Next action:** parent verifies the new fixture through full exact-head CI and delivers the reviewed candidate.
- **Resolution condition:** block 4 has no skip, its fixture exactly matches the source fence, and all four verifier layouts copy it into Infrastructure for compilation.
- **Verification evidence:** byte-identity, complete manifest coverage and authored/Claude/Codex/package gate-setup tests pass. The manifest now selects 47 fences for compilation and retains 11 explicit skips. Block 2 remains skipped with a corrected reason naming its missing builder API and leaf contracts; no registration implementation was invented. Actual compiler validation and delivery remain pending.

## B011

- **Kind:** bug
- **Observed/reported:** 2026-10-13. Independent frozen review of `9559be3` found captured primary-constructor parameters in the checkout, seeder and `Scoped<T>` manifest support wrappers. Cause confirmed: their methods read constructor parameters without the explicit readonly dependency fields required by the applicable style contract. Parent support inspection also found shadowing output parameters that forced non-constructor `this.` reads, empty runtime string literals, legacy extension syntax and primary-constructor repository dependency initializers.
- **Impact and priority:** P2; the standards verification support code violates the dependency-field convention it claims to demonstrate.
- **Source owner:** `tj-agents/dotnet` scaffold snippet manifest headers and shared support types.
- **State:** resolved
- **Repair link:** `plans/single-standard-conventions/GOAL.md`, branch `Fix/SnippetsCompileUnderScaffold`, and `reviews/Fix-SnippetsCompileUnderScaffold.md` finding SSN-3.
- **Next action:** parent completes independent incremental review, full exact-head CI and delivery.
- **Resolution condition:** these three wrappers use explicit private readonly fields assigned in ordinary constructors, with `this.` only on shadowed constructor assignments; their snippet regions remain byte-identical to the contract fences. Shared support types use bare field reads, `string.Empty` for actual empty strings, C# 14 extension blocks, explicit readonly repository dependency fields and one file-scoped namespace per support file.
- **Verification evidence:** corrected wrappers and shared support types are regenerated across all four layouts. Eight snippet tests pass, including per-fence identity and complete host asset/setup checks; source layout, kit 1.2.1 and generated freshness checks pass. Actual compiler validation and delivery remain pending.

## B012

- **Kind:** bug
- **Observed/reported:** 2026-10-13. Exact-head Scaffold PR run `38437895854` at `565a6eddb306c2f705a544e68d3fb856e2cbf871` reaches snippet compilation and reports five E2E diagnostics: MA0002 on the seed dictionary constructor and MA0004 on four `ClockSteps` awaits. Cause confirmed: the E2E support dictionary omits a string comparer and the actual source contract example omits `ConfigureAwait(false)` under the existing analyzer policy.
- **Impact and priority:** P2; the contract snippet gate fails and blocks delivery of this standards branch.
- **Source owner:** `tj-agents/dotnet` `testing/e2e` contract and scaffold E2E snippet support.
- **State:** in-progress
- **Repair link:** `plans/single-standard-conventions/GOAL.md`, branch `Fix/SnippetsCompileUnderScaffold`, and the CI repair boundary in `reviews/Fix-SnippetsCompileUnderScaffold.md`.
- **Next action:** parent runs full exact-head Scaffold CI, completes independent incremental review and delivers the corrected candidate.
- **Resolution condition:** the four awaits in the actual contract use `ConfigureAwait(false)`, the support dictionary uses `StringComparer.Ordinal`, regenerated fixtures remain verbatim with an empty manifest header, and full exact-head compilation passes without analyzer suppression.
- **Verification evidence:** the archived CI log `6edcc2377fa126d3-repair-scaffold-ci-failure.log` identifies E2E.Stubs.cs line 13 and ClockSteps fixture lines 30, 31, 32 and 38. All eight snippet tests and three source-layout tests pass after repair; both generators and freshness checks pass for all 585 generated outputs. The affected-source check verifies all five corrected expressions and the empty header/no-skip entry. No local dotnet or Terraform process ran; actual compiler qualification and delivery remain pending.

## B013

- **Kind:** bug
- **Observed/reported:** 2026-10-16. The .NET scaffold required Core's retired capabilities adopter, so it could not use the current `machine:plugin-lock` interface.
- **Impact and priority:** P2; current Core could not prepare standards for a new scaffolded project.
- **Source owner:** `tj-agents/dotnet` `.agents/dotnet/utility/scaffold`.
- **State:** resolved
- **Repair link:** PR #54, merged at `728b3049ef5b69fc7e3af5a3ab2ddc3cf2edde55`.
- **Next action:** none.
- **Resolution condition:** current Core writes a valid `.agents/plugins.lock.json` and host settings for scaffolded .NET and Azure projects, and scaffold CI passes.
- **Verification evidence:** real adoption dry run passed locally; Linux and Windows scaffold verification, Template conformance, generated freshness and host checks passed on PR #54 before merge.
