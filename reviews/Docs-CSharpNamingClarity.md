# Code review â€” Docs/CSharpNamingClarity

**Review status:** `complete`
**Reviewed up to commit:** `63f38d6c0331bafdda16c55c6c9d92c4a899f026` `(2026-09-30)`
**Judgment:** `approved`

## Review pass â€” 2026-09-29 â€” docs

**Candidate base:** `a891af4c48bcbc302602e7a57ccd8d6899305fdd`
**Candidate head:** `ca1a052ccae37cc875dc29a2855cddec2d6e0e65`
**Candidate branch:** `Docs/CSharpNamingClarity`
**Candidate scope:** `all`
**Candidate path-set:** `sha256:aba64f982988dcc31a0f59074ba852c0651e8d8deff3d6f7a92bb92d5240394e` `(2 paths)`
**Candidate patch:** `sha256:e71abc5675fae5b9134119c1f878efe96d5e99981ff91c85835e26b0949bdb1f`
**Candidate bundle:** `C:/Users/TOMMYS~1/AppData/Local/Temp/dotnet-naming-review-c7v3xiim`
**Candidate bundle identity:** `sha256:2c43fd591032279ab083f845673c7a055bd1f1e786dc22c4c9caa0de664c8a89`
**Work-order path:** `reviews/Docs-CSharpNamingClarity.md`
**Work-order mode:** `new`
**Pass judgment:** `approved`

### Findings

No findings. Parent fallback after the configured review-lens model was unavailable in this session.
The authored definition and generated distribution are byte-identical. The new rule preserves domain,
locking and identity distinctions, avoids a blanket shortening rule, and does not require new abstractions.
The example uses generic repository vocabulary and introduces no Concertable dependency. Existing suffix,
profile, prerequisites and capability implementation rules remain intact. The direct Microsoft source
supports readable names; composite query naming is explicitly house guidance.

Validation: generator check passed; source-layout/safety tests passed 13/13 using the installed PowerShell
executable; both AGENTS/CLAUDE pairs are valid; git diff --check passed. Initial local failures were corrected
by LF-normalizing the edited source and selecting the real pwsh executable ahead of the global-tool shim.

## Review pass â€” 2026-09-29 â€” naming concern split

**Candidate base:** `ca1a052ccae37cc875dc29a2855cddec2d6e0e65`
**Candidate head:** `6f6da0bae214403d3017e353887a0d884a1dad82`
**Candidate branch:** `Docs/CSharpNamingClarity`
**Candidate scope:** `all`
**Candidate path-set:** `sha256:08f60cc750ccd54193006ec9e2aa06bf066115a825560941ffb8d95b7629adbb` `(43 paths)`
**Candidate patch:** `sha256:c33d393dcc11c75b4ac27922b6a5e5256fe18905dbbe730605b28f3afc6d09bc`
**Candidate bundle:** `C:/Users/TOMMYS~1/AppData/Local/Temp/dotnet-naming-split-review-qcc7bksr`
**Work-order path:** `reviews/Docs-CSharpNamingClarity.md`
**Work-order mode:** `append`
**Pass judgment:** `approved`

Native review is unavailable; the configured independent read-only lens is selected for the frozen candidate.

### Findings and validation

No retained findings. The configured independent lens failed because its model is unsupported by this
account. The parent completed the native/general and concern-ownership fallback; no independent review
success is claimed. The frozen diff preserves the existing naming semantics while placing shared
identifiers, collaborators, data shapes and mapping in separate owners. EF/HTTP/RPC requirements remain
conditional; read/write/combined capabilities and visibility are distinguished. Resolve retains its
operation meaning. The former explicit Facts blacklist is replaced by positive responsibility/shape
conventions. The core roster changes atomically with generation and test expectations.

Generator parity and all 13 source-layout/safety tests passed. Frozen-tree Markdown skill links and
AGENTS/CLAUDE pairs resolve. Both host manifests and the generated selection catalog include the changed
owners. Representative routing: repository -> persistence (+ multitenancy when selected); resolver ->
collaborator-naming; DTO -> data-contract-naming; conversion -> mapping; HTTP -> http-api; RPC -> proto.
No product rule or installed-cache edit was introduced. The repository has no docs_reachability helper;
its absence is not reported as a pass.


## Review pass â€” 2026-09-29 â€” repository capability qualifiers

**Candidate base:** `6f6da0bae214403d3017e353887a0d884a1dad82`
**Candidate head:** `66f27c5c9bc673a0aeba315340314cc7a2a30e21`
**Candidate branch:** `Docs/CSharpNamingClarity`
**Candidate scope:** `all`
**Candidate path-set:** `sha256:34d591529a6be801ef92844ad36d44706b6c7f775bf63568758fa103aac58547` `(4 paths)`
**Candidate patch:** `sha256:ebebb989a5a4b69878a18cc288a01289fe56364ab7511e8bf17d6821325cd31d`
**Candidate bundle:** `C:/Users/TommySeery/source/repos/tj-agents/dotnet/.git/agent-workflow/runs/naming-capability-20260929/review/23ace2a3cc55a5c6cb420fca9b5bb99f99cf809be20a038873e6c291c5146f3f`
**Candidate bundle identity:** `sha256:5f4453435f193a179eacc649f77d522f7abdb0e6db48f5dd76af0bbf66003351`
**Work-order path:** `reviews/Docs-CSharpNamingClarity.md`
**Work-order mode:** `append`
**Pass judgment:** `approved`

### Findings

No retained findings. The parent completed native/general, contradiction and concern-ownership checks against the frozen four-file delta. The configured review-lens is known unavailable in this session because its model is unsupported; no independent review is claimed.

Persistence owns the capability exposed by an interface. Multitenancy owns the visibility qualifier and demonstrates its composition with that capability. A query-only privileged contract keeps Read even when its implementation needs a writable context for an existing transaction. Combined privileged repositories remain combined. Projection examples also retain their exposed read capability. This resolves the prior contradiction without selecting a new architecture or changing context implementation requirements.

Validation: required generator check passed (107 files / 33 definitions), frozen source/generated parity and changed Markdown links passed, patch identity matched and diff whitespace passed. The earlier 13 source-layout/safety tests remain the last full source test pass; these four prose/mirror changes did not alter generation logic or profile metadata. This repository has no docs_reachability helper, and its absence is not a passed check. The disposable candidate bundle is removed after completion.


## Review pass â€” 2026-09-30 â€” responsibility ownership

**Candidate base:** `66f27c5c9bc673a0aeba315340314cc7a2a30e21`
**Candidate head:** `0560e42b13168bc94b1a2ea56dec22e637c2f769`
**Candidate branch:** `Docs/CSharpNamingClarity`
**Candidate scope:** `all`
**Candidate path-set:** `sha256:3c0eb7e82c857efc7f47c4e36cb4a288be3178f763f8e36b0f52f28d095bbc20` `(12 paths)`
**Candidate patch:** `sha256:818b29b848b154d491fd9880a9154bd869c6f73d000c89b43a76e00ca49edb6d`
**Candidate bundle:** `C:/Users/TOMMYS~1/AppData/Local/Temp/party-responsibility-standards-review-6qqy8yld`
**Work-order mode:** `append`
**Pass judgment:** `approved`

The earlier review missed a responsibility error: persistence explicitly allowed resolution methods
on repositories, and shared naming treated the verb independently of the component's responsibility.
That earlier conclusion is superseded for this rule. The correction assigns queries, projections,
persistence and locks to repositories; resolution rules and expected-actor validation belong to resolvers.
It requires implementation separation before renaming contracts. Read/write/combined capability names,
conditional profiles, DTO and transport ownership remain intact. No word blacklist or new architecture
is introduced. Both host manifests and the Claude marketplace describe the same changed standard.

The parent reviewed the frozen diff and its responsibility, contradiction and generated-parity concerns.
The previously unavailable configured lens remains unavailable; this is not an independent review.
No retained findings. Validation: 8 source-layout tests, generator parity (107 files/33 definitions),
changed skill links, frozen source/mirror parity, paired instruction files and diff whitespace passed.
No generator code changed. Publication and installation remain held. The disposable bundle is removed
after this completed pass; the hashes above retain the candidate identity.


## Review pass â€” 2026-09-30 â€” canonical role and outcome contracts

**Candidate base:** `0560e42b13168bc94b1a2ea56dec22e637c2f769`
**Candidate head:** `6863c77645c17c3131e61171a538a85b83ae5ac7`
**Candidate branch:** `Docs/CSharpNamingClarity`
**Candidate scope:** `all`
**Candidate path-set:** `sha256:66ce9ef7b7c204d113e008ace57b3b7a7104cb6f063b61216417a13ee48f8d56` `(35 paths)`
**Candidate patch:** `sha256:bb1bc38f8fe3e57229a431dce751287da06e35515e747b6bc8508112f1e91d45`
**Candidate bundle:** `C:/Users/TOMMYS~1/AppData/Local/Temp/party-canonical-contracts-final-standards-review-egt9v_s4`
**Work-order mode:** `append`
**Pass judgment:** `approved`

The earlier responsibility correction still omitted the relationship between a collaborator role and
its returned outcomes, and left generic repository naming behind the EF Core applicability gate.
This pass reviews the structural correction, rather than adding an incident-word prohibition.

The parent reviewed the immutable source delta, dependency/applicability routing and generated package.
The previously unavailable configured independent lens remains unavailable; this is the recorded parent
fallback. No retained findings. Shared naming routes each concern to its owner. Collaborator contracts
define subject, responsibility, operation, success value and alternate outcomes together. The new
repository-naming skill is core/stack-free and owns read/write/combined capability names, query/write
verbs and storage returns. EF-specific aliases, context binding, transaction mechanics and model mapping
remain in persistence. Payload, result, validation, mapping, DI and transport concerns retain their
separate owners. Generic role semantics are house conventions; concrete library contracts are conditional.

The result owner now distinguishes a persistence boundary from a collaborator implemented in a project
called Infrastructure. Resolver present/absent APIs use Option under Reunion; named failures use typed
Result; validators use their selected validation result and boolean questions use bool. Validator method
and file examples were corrected consistently. DTO properties and local/provider nullable values keep
their separate meaning. The change adds no product-specific rule or new architecture requirement.

Generation updates seven-member core selection, both host adapters, manifests, packaged definitions and
index atomically: 110 files from 34 definitions. All 13 source-layout/generation-safety tests passed.
Frozen source/mirror parity, changed skill links, instruction pairing, profile selection and diff checks
passed. The initial parity failure was CRLF authored files versus LF generated copies; source line
endings were normalized and the required suite rerun successfully. Generator changes only expand the
explicit supported core roster; safety logic remains intact. README now exposes the physical owner map.

The final scope is 35 paths, 627 additions and 271 deletions including generated artifacts. The earlier
f505fcf snapshot is superseded by this cumulative candidate. Disposable review bundles are removed
after completion. Source is locally committed; publication and installation remain held.


## Review reconciliation â€” 2026-09-30 â€” current main for draft publication

Candidate head: `e875bfc956bfd0ca1f1d4eea6f825d7273d83bde`; base:
`b693fe48ccd8649d36320e092bb2b8dcf46f0a31`. The conflict-free main merge moves the tier declaration
to .agents/tiers, reserves that directory in discovery, accepts supported tier-schema fields, and adds
the main-owned cross-repository payload CI check. The user explicitly requested draft publication.

The parent inspected the exact 6863c77..e875bfc reconciliation diff. Every authored naming/result/
validation definition and generated mirror is unchanged. The tier declaration and workflow match main;
the generator retains this branch's seven-member core profile and safety checks alongside the incoming
tier-path update. No retained source findings; no independent review is claimed.

All 13 source-layout/generation-safety tests pass, generator -Check reports 110 current files from 34
definitions, and whitespace checks pass. Source is clean. The full PR is 53 changed paths against main.
Draft publication is authorized; merging and consumer installation remain held. Remote CI is pending.

### Draft publication and inherited CI gate

Draft https://github.com/tj-agents/dotnet/pull/31 and refreshed origin/Docs/CSharpNamingClarity both
carry e875bfc956bfd0ca1f1d4eea6f825d7273d83bde. Source tests and generated parity pass locally.
PR run 36760215433 fails while the unchanged main workflow checks out tj-agents/core: GitHub returns
Not Found. Main run 36735653400 at b693fe48 reproduces the identical checkout error. This is not a failing
naming assertion. The Windows matrix job was cancelled after the Ubuntu failure.

Owning infrastructure gate: the dotnet CI workflow's cross-repository checkout needs authorized read
access to tj-agents/core. Resolution condition: checkout succeeds and both OS verification jobs pass on
the candidate head. No credentials, token scopes, checks or assertions were changed. The canonical
Party Foundation progress ledger retains this external gate; the PR body links both failed runs.
Draft review is published; merge and installation remain held.

## Review pass — 2026-09-30 — DDD ownership and discovery

**Candidate base:** `e875bfc956bfd0ca1f1d4eea6f825d7273d83bde`
**Candidate head:** `63f38d6c0331bafdda16c55c6c9d92c4a899f026`
**Candidate branch:** `Docs/CSharpNamingClarity`
**Candidate scope:** `all`
**Candidate path-set:** `sha256:bc0808e519cb29d88abb3e55fcc65995804b3b8cfa2cb1d518124e305128a645` `(23 paths)`
**Candidate patch:** `sha256:6512614070adff54cd57ed2d522b5c21f295da08cbde3702e582940a3f848a21`
**Candidate bundle:** `C:/Users/TOMMYS~1/AppData/Local/Temp/party-ddd-review-97idk3uh`
**Candidate bundle identity:** `sha256:7aef88d18e9da05e3d7e7fa499f780d29c27b4caa48822741289e4629511555a`
**Work-order path:** `reviews/Docs-CSharpNamingClarity.md`
**Work-order mode:** `append`
**Pass judgment:** `approved`

Synchronized once before review: origin/main `b693fe48ccd8649d36320e092bb2b8dcf46f0a31;`,
with zero missing base commits. Review covers the committed incremental standards correction only.

The configured native-general review lens failed before reviewing: gpt-5.3-codex-spark is unsupported
for this account. The parent performed the native/general and domain-ownership/discovery checks over
the same frozen bundle. This pass is a parent fallback, not an independent review. No retained findings.

The 23-path correction consists of 9 authored paths and 14 generated paths. DDD and value semantics
were present and unchanged before this correction; the defect was incomplete semantic routing and
ambiguous behavior ownership in the new naming concerns. The original DDD body is retained verbatim,
with one added domain-service/application-orchestration section. Value semantics, repository naming,
result carriers, validation, profile rosters and generated selection metadata are unchanged. Shared
naming, collaborator and mapping tasks now reach their domain/value owners; data-contract naming
identifies transferred shapes. Architecture selection remains optional and B2B resolver contracts are
outside the changed paths.

Validation: all 13 source-layout/generation-safety tests pass using the actual PowerShell executable;
110 generated files from 34 definitions match; authored/package semantic routes and both host adapters
resolve; changed local links, instruction pairing and diff whitespace pass. The original attempt selected
the global PowerShell shim, so the wrapper test failed before its intended Python check. Correcting the
runner environment resolved it without source/test changes. The frozen tier gate reports no applicable
stack tier. There is no repository skill router or workflow runtime. The immutable bundle identities
were verified; its disposable files are removed after this completed pass.

At the reviewed head, remote run `36764633028` passed generation/source checks on both OS jobs,
then reproduced the private `tj-agents/core` checkout `Not Found` gate (Ubuntu failed; Windows cancelled).
The payload-shape check remains unexecuted. B2B #38 run `36759326771` independently supplies provider
passes at `7069315a783bfea463abf64f098fcc9ded43cb0b`: 892 backend tests, including Tenant integration 99/99,
with no skips. Its image vulnerability scan remains red. These results do not qualify descendant heads.
No merge or installed-cache change is included.

## Review pass — 2026-10-01 — namespace-aware type names

**Candidate base:** `63f38d6c0331bafdda16c55c6c9d92c4a899f026`
**Candidate head:** `ebdc0d66c82e18ca4b9e162d1a60b8dec0f2719a`
**Candidate branch:** `Docs/CSharpNamingClarity`
**Candidate scope:** `all` (10 changed paths)
**Pass judgment:** `approved`

No retained findings. The parent reviewed the committed, bounded correction for wording, ownership,
contradictions and generated parity; no independent review is claimed. `csharp-naming` owns the shared
namespace-context rule. Its example keeps `OrderRepository` as a meaningful subject and role, preserves
framework and published names and real strategy distinctions, and resolves rare call-site ambiguity with
qualification or aliases. The rule explicitly covers fixtures, tests and plan snippets. The two host
manifests and Claude marketplace retain matching discovery descriptions; generated adapters and plugin
copies come from the supported generator.

Validation: generator wrote 110 files from 34 definitions and `-Check` reported no drift. All 13
source-layout/safety tests passed when the real PowerShell executable was placed first in the test
process PATH. The first test invocation selected the global-tool shim and failed before the wrapper's
Python assertion; no source or test change was needed. Changed local links, AGENTS/CLAUDE pairs and
commit whitespace checks passed. The ten-file correction is locally committed as `ebdc0d6`.
Publication, merge and consumer installation remain held. PR #31's inherited private `tj-agents/core`
checkout gate remains outside this correction.

## Review pass — 2026-10-01 — namespace-aware type names

**Candidate base:** `63f38d6c0331bafdda16c55c6c9d92c4a899f026`
**Candidate head:** `ebdc0d66c82e18ca4b9e162d1a60b8dec0f2719a`
**Candidate branch:** `Docs/CSharpNamingClarity`
**Candidate scope:** `all` (10 changed paths)
**Pass judgment:** `approved`

No retained findings. The parent reviewed the committed, bounded correction for wording, ownership,
contradictions and generated parity; no independent review is claimed. `csharp-naming` owns the shared
namespace-context rule. Its example keeps `OrderRepository` as a meaningful subject and role, preserves
framework and published names and real strategy distinctions, and resolves rare call-site ambiguity with
qualification or aliases. The rule explicitly covers fixtures, tests and plan snippets. The two host
manifests and Claude marketplace retain matching discovery descriptions; generated adapters and plugin
copies come from the supported generator.

Validation: generator wrote 110 files from 34 definitions and `-Check` reported no drift. All 13
source-layout/safety tests passed when the real PowerShell executable was placed first in the test
process PATH. The first test invocation selected the global-tool shim and failed before the wrapper's
Python assertion; no source or test change was needed. Changed local links, AGENTS/CLAUDE pairs and
commit whitespace checks passed. The ten-file correction is locally committed as `ebdc0d6`.
Publication, merge and consumer installation remain held. PR #31's inherited private `tj-agents/core`
checkout gate remains outside this correction.
