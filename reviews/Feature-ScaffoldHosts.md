# Code review - Feature/ScaffoldHosts

**Review status:** `complete`
**Reviewed up to commit:** `8f22d5d772e61d30b0d94dd97952bacfd0ec4f41` (2026-10-12)
**Security-reviewed up to commit:** `8f22d5d772e61d30b0d94dd97952bacfd0ec4f41` (2026-10-12)
**Judgment:** `approved`

## Review pass - 2026-10-12 - full

**Candidate base:** `d6c3461cd251a8805554acd79b56e1cecb7825fc`
**Candidate head:** `1a87313b0ae5650bef89825ad501def946523741`
**Candidate branch:** `Feature/ScaffoldHosts`
**Candidate scope:** `all`
**Candidate path-set:** `sha256:67c6776da7550443f76c3385a6c975772961a551efbeef3a13f6be21361c97d4` (131 paths)
**Candidate bundle:** `C:\Users\TommySeery\AppData\Local\Temp\review\PSTM8AB1s3BlfTY0G50GkB\UP6fLzZneXqVwubqSqQOct\uw6aON6R52isSqbtClYiyE`
**Candidate bundle identity:** `sha256:51d87b793d57c80280ac60570d4b48ce96316320041d57e405342928f164c873`
**Candidate descriptor:** `C:\Users\TommySeery\source\repos\tj-agents\dotnet\.git\agent-workflow\runs\scaffold-hosts-20261012\review\bb0e9a38de91e768ac4aa6ed0a5622c84dab84fdacee8c17d35afa4594a124d8\descriptor.json`
**Candidate patch identity:** `sha256:137c5a3f6ce91785a76da55b4f08576c5665c700630380bbe7e3561a47b492d3`
**Work-order path:** `reviews/Feature-ScaffoldHosts.md`
**Work-order mode:** `new`
**Pass judgment:** `changes-requested`

The final synchronization retained the exact candidate and delivered base. The native L4 layer and
fresh independent L4 correctness/workflow plus L2 security contexts receive this immutable range.
Security is selected explicitly for the newly generated fixture authentication and container/database
configuration; generic classifier paths are empty. No migration or production schema is introduced.
Tier resolution returned 36 dotnet conventions; relevant frozen root/nearest instructions and
build, style, structure, dependency-injection, persistence and integration guidance govern the pass.
Repository route violations and routed identities are empty. Installed engineering review lifecycle
was loaded from its canonical package source; the helper cannot record an external package body
through its repo-contained skill identity API, so no fabricated repository skill entry is supplied.

### Findings

Parent synthesis retains SEC3 and the compiler defect independently confirmed by the exact-source verifier. The fresh L4 correctness/workflow lens found no further actionable defect; the fresh L2 security lens confirmed SEC3 and preserved fixture/authentication boundaries across132 selections. Native review completed at the frozen identity.

- [x] **SEC3 - MEDIUM - security local configuration** - `.agents/dotnet/utility/scaffold/components/functions/files/src/$NAME$.Functions/local.settings.json:2`
  Functions local settings are plaintext and receive storage/database configuration, while the generated consumer .gitignore omits local.settings.json. After configuring real local credentials, an ordinary git add/publish can disclose them. Add a recursive basename ignore rule and generated-output regression. The immutable security lens verified 132 selections, archive/path/mirror identities and the sandbox plaintext connection-string output. Repair remains with the existing Slice4 writer; linked problem record B004.

- [wontfix] **VER1 - MEDIUM - generated compilation** - `.agents/dotnet/utility/scaffold/components/opentelemetry/component.json` and integration fixture contributions/templates
  The accepted Sandbox preset fails compilation: Functions tracing lacks an accessible OpenTelemetry WithTracing extension; ApiFixture lacks the ConfigureTestServices import, uses obsolete Testcontainers constructors and omits required ConfigureAwait(false). Repair the generated dependencies/imports/awaits and verify Sandbox plus SQL/JWT and Dapper/hybrid fixture branches using checked per-command results. B003 owns the repair, with final seven-row Windows/Ubuntu qualification retained by the aggregate goal.

### Native evidence reconciliation

Native returned three compile hypotheses. Parent excludes each against the independently observed authored verifier log: direct Azure.Functions.Sdk/1.0.1 restore succeeded (line250), API compilation emitted SandboxSample.Api.dll (line263), and worker compilation emitted SandboxSample.Worker.dll (line264). The approved Functions MSBuild SDK is supported; the emitted C#14 semicolon partial Program declarations compile; the worker OpenTelemetry receiver also compiles. Duplicate API visibility substitution is harmless to compilation but unintended and will be removed by the existing writer. The actual failure is retained as VER1 rather than substituting these contradicted premises.

All35 Python tests passed against current core0d797f568a53b73ff2e8c271c7aaf3f32f29035e. Exact generator check327 outputs, frozen pinned-kit1.2.1 and180 source/host/plugin payload comparisons passed. The full local verifier passed its first five rows and failed Sandbox; it did not reach the final SQL fixture row. No live Docker, schema reset or authentication outcome is claimed.

## Agent-host coverage

```agent-host-coverage
{
  "schema_version": 1,
  "shared_source": ".agents/dotnet/utility/scaffold",
  "candidate_head": "8f22d5d772e61d30b0d94dd97952bacfd0ec4f41",
  "hosts": [
    {
      "host": "claude",
      "behavior": "Resolve the shared scaffold guidance and invoke the identical packaged Python renderer.",
      "source": ".agents/dotnet/utility/scaffold/SKILL.md and scripts/scaffold.py with component/template payloads",
      "mapping": ".claude/skills/scaffold and plugins/dotnet/skills/scaffold",
      "verification": {
        "level": "source",
        "result": "passed",
        "evidence": "Exact8f22d5d: native L4 incremental and fresh cumulative L2 security are clear. All36 repository tests passed against corec91b60c9;327-output wrapper, frozen kit1.2.1,180 payload comparisons and6 instruction pairs passed. Scaffold push38303051185 and PR38303056095 both pass seven restore/build/test configurations on Windows/Ubuntu with no testhost aborts; generic ci38303056882 hosts/Windows/Ubuntu also passes. Both content-bound Dapper/PostgreSQL and hybrid/SQL builds have zero warnings/errors; two no-container binding probes pass. Source/static host coverage; no live Docker/auth/schema claim."
      }
    },
    {
      "host": "codex",
      "behavior": "Resolve the shared scaffold guidance and invoke the identical packaged Python renderer.",
      "source": ".agents/dotnet/utility/scaffold/SKILL.md and scripts/scaffold.py with component/template payloads",
      "mapping": ".codex/skills/scaffold and plugins/dotnet/skills/scaffold",
      "verification": {
        "level": "source",
        "result": "passed",
        "evidence": "Exact8f22d5d: native L4 incremental and fresh cumulative L2 security are clear. All36 repository tests passed against corec91b60c9;327-output wrapper, frozen kit1.2.1,180 payload comparisons and6 instruction pairs passed. Scaffold push38303051185 and PR38303056095 both pass seven restore/build/test configurations on Windows/Ubuntu with no testhost aborts; generic ci38303056882 hosts/Windows/Ubuntu also passes. Both content-bound Dapper/PostgreSQL and hybrid/SQL builds have zero warnings/errors; two no-container binding probes pass. Source/static host coverage; no live Docker/auth/schema claim."
      }
    }
  ]
}
```

VER1 disposition: compiler/linter failures belong to the owning qualification gate under review Stage7. This confirmed defect is already recorded as B003 and actively repaired in the same slice; it is carried there rather than counted as a retained source-review finding. SEC3 remains the one retained review finding. The full verifier is mandatory before readiness.

## Review pass - 2026-10-12 - incremental

**Candidate base:** `1a87313b0ae5650bef89825ad501def946523741`
**Candidate head:** `d57396774117027c854d7b7a773f71a08366e67b`
**Candidate branch:** `Feature/ScaffoldHosts`
**Candidate scope:** `all`
**Candidate path-set:** `sha256:f320dd58ca8188506b11a75313e69c9e6c23ba70fd0b25c6eb109e178bd27919` (47 paths)
**Candidate bundle:** `C:\Users\TommySeery\AppData\Local\Temp\review\PSTM8AB1s3BlfTY0G50GkB\UP6fLzZneXqVwubqSqQOct\Ciio44HxwgF97C86DEqQzZ`
**Candidate bundle identity:** `sha256:a822f887d077b1cc3247ab32eb464380a50df187c694845600d3b60cf5e2d23b`
**Candidate descriptor:** `C:\Users\TommySeery\source\repos\tj-agents\dotnet\.git\agent-workflow\runs\scaffold-hosts-20261012\review\0a28a8e381f1c2017dec2f3a0c4a90cd9528c3d009a5c8617a38327408b0176f\descriptor.json`
**Candidate patch identity:** `sha256:2d21a31900f49a898ebf67403c7c51d43442e8b1c7332bf15b766bb29d4fed75`
**Work-order path:** `reviews/Feature-ScaffoldHosts.md`
**Work-order mode:** `append`
**Pass judgment:** `changes-requested`

### Findings

Synthesis pending. This pass covers host/fixture corrections, shared instruction-pointer correction, generated projections and B003/B004/B005/B006/M001 records. Actual base remains delivered d6c3461; fresh fetch observed behind0/ahead2 before the pointer checkpoint. Mandatory native uses the completed watermark; fresh L2 security covers cumulative d6c3461..d573967 for fixture/local-configuration changes despite empty classifier paths. Parent owns bounded workflow/doc consistency. Independent full current-core/seven-row qualification is actively owned at this exact head. The earlier081e831 preparation was replaced before work-order write or review dispatch when the inherited consumer pointer assertion failed; no completed judgment was rewritten.


Incremental synthesis completed at exact d573967. Native review returned no actionable regressions; its read-only full verifier attempt hit NuGet.Config access, while the independent retained qualification actually completed all36 current-core tests and all seven local rows. Fresh cumulative L2 security confirms SEC3 is fixed: Git check-ignore matches the basename rule and Functions SDK prevents publishing local.settings. No production fixture-authentication leakage was found. It identifies SEC4 below; the original full-pass judgment remains unchanged.

- [x] **SEC4 - MEDIUM - integration container credentials** - `.agents/dotnet/utility/scaffold/components/integration-postgres/component.json:8` and `integration-sqlserver/component.json:8`
  Bare Testcontainers4.16 builders use known administrator credentials and publish ports without HostIP. If a generated fixture starts on a reachable Docker host, an attacker can authenticate to the temporary database and read/tamper with test data or disrupt it. Exact installed assembly IL establishes both defaults and binding conversion. Generate cryptographically random per-fixture passwords and loopback publication; keep any remote-daemon extension deliberate. B007 owns repair within PR47. No production database or host compromise is claimed.

SEC3 resolution evidence: fresh independent L2 validated all464 archive files and cumulative141-path identity, all60 payloads across three mirrors, nine rendering profiles with test-only auth isolation, actual Git ignore rule and installed Azure.Functions.Sdk1.0.1 CopyToPublishDirectory=Never.

Platform qualification at d573967: exact Scaffold push38295683230 and PR38295690036 plus ci38295690678 all completed success at attempt1. Both Scaffold jobs on Windows/Ubuntu execute all seven restore/build/test rows; each OS has seven Build succeeded receipts and no testhost/abort markers. Minimal has no test assembly and its unconditional dotnet test exits successfully. Sandbox direct Functions restore precedes solution restoration. Complete logs retained as scaffold-hosts-pr47-38295683230.log and scaffold-hosts-pr47-38295690036.log in Temp. Corrected-source qualification remains owned before readiness.

## Review pass - 2026-10-12 - incremental

**Candidate base:** `d57396774117027c854d7b7a773f71a08366e67b`
**Candidate head:** `8f22d5d772e61d30b0d94dd97952bacfd0ec4f41`
**Candidate branch:** `Feature/ScaffoldHosts`
**Candidate scope:** `all`
**Candidate path-set:** `sha256:c1d6367ef7226c23ad298ff0d49dabfe91048e64336985cd8db8deb6e272800b` (14 paths)
**Candidate bundle:** `C:\Users\TommySeery\AppData\Local\Temp\review\PSTM8AB1s3BlfTY0G50GkB\UP6fLzZneXqVwubqSqQOct\xzHbRriXV3BtGA0OYsUQeS`
**Candidate bundle identity:** `sha256:befc125cbd2ea386b04ae556844871d64b33e998109cb41c83db5a7deeee40fe`
**Candidate descriptor:** `C:\Users\TommySeery\source\repos\tj-agents\dotnet\.git\agent-workflow\runs\scaffold-hosts-20261012\review\c731db46b89757706d180d0e62c510792c7a7038a03a747751aa9a0f598c7657\descriptor.json`
**Candidate patch identity:** `sha256:9d440962e83de1f599c3513d8fbc9e743fe2b2dbc228de07a79d62c482a7ed34`
**Work-order path:** `reviews/Feature-ScaffoldHosts.md`
**Work-order mode:** `append`
**Pass judgment:** `approved`

### Findings

Synthesis pending. L4 native reviews the completed d573967 watermark delta; fresh L2 security independently reviews the cumulative delivered-base range for changed integration credentials/bindings and preserved fixture-only authentication. Parent owns the bounded workflow/record consistency lens. Source is released and clean except this work order; no source changes occur during frozen review. The existing SEC4 text/severity and earlier pass judgment remain immutable.


Final incremental synthesis: Exact8f22d5d: native L4 incremental and fresh cumulative L2 security are clear. All36 repository tests passed against corec91b60c9;327-output wrapper, frozen kit1.2.1,180 payload comparisons and6 instruction pairs passed. Scaffold push38303051185 and PR38303056095 both pass seven restore/build/test configurations on Windows/Ubuntu with no testhost aborts; generic ci38303056882 hosts/Windows/Ubuntu also passes. Both content-bound Dapper/PostgreSQL and hybrid/SQL builds have zero warnings/errors; two no-container binding probes pass.

SEC4 resolution: fresh independent L2 validated all four supplied artifact hashes, exact Git patch,464 archive files/blobs and60 payloads across all mirrors. Twelve database/data/auth renders preserve test-only header authentication. Fixture passwords use24 CSPRNG bytes with SQL complexity prefix; both providers bind their sole random host port to127.0.0.1. Independent installed Testcontainers4.16 IL confirms overriding one binding and modifiers before container creation. No actionable security defects remain in cumulative d6c3461..8f22d5d. Functions ignore/publish protections remain verified. No live container/auth/schema execution is claimed.

Native process completed with exit0 and no actionable defect. Its optional generated-copy Get-FileHash command failed in its shell; parent immutable Git/archive comparison and independent464-file/60-payload validation actually establish mirror identity. The optional diagnostic is not claimed as a pass.

Parent workflow/record consistency is clear. B003/B005/B007/M001 resolution conditions are met by final source-bound receipts. Local inert ledger closeout records the results without altering the published executable candidate; core committing/remote-validation prohibit another observation-only push. Earlier pass judgments remain immutable.
