# Code review — Fix/IdempotencyHashAndValueStructs

> **This file is a work order, not a discussion.** If you're handed this file, fix the open `[ ]`
> findings directly and report what changed. Tick each `[x]` as you land it. Pause only for a genuinely
> irreversible or ambiguous finding: record its durable disposition, take the safe path, and keep going.

**Review status:** `complete`
**Reviewed up to commit:** `a0ac736493407105e9a6ae357c8d80ed8ecf0646`  `(2026-10-05)`
**Judgment:** `approved`

## Review pass — 2026-10-04 — docs

**Candidate base:** `14642919f4feedb472aaade2badb414e31baf501`
**Candidate head:** `4517d01020130a109ad0959364575f97eb7a7154`
**Candidate branch:** `Fix/IdempotencyHashAndValueStructs`
**Candidate scope:** `all`
**Candidate path-set:** `sha256:512e4f799ff543521178e33bac800fa5407fd89ec32f1c90a1312372e53aba1f` `(8 paths)`
**Candidate bundle:** `C:\Users\TommySeery\source\repos\tj-agents\dotnet\.git\agent-workflow\runs\idemhash-docs-review-1\review\7f4d8082ff1a8f6fa8d981ee2e182c742bb781a50432f73febb20c00deb96974`
**Candidate bundle identity:** `sha256:89bba542b172c25176620c2411afcc56e3f22ba735d753e11e785f3f6d67aa1a`
**Work-order path:** `reviews/Fix-IdempotencyHashAndValueStructs.md`
**Work-order mode:** `new`
**Native layer:** `code-review` skill (medium); lenses: accuracy+contradiction, one-rule-one-home+concision+followability; docs reachability 0 errors
**Pass judgment:** `changes-requested`

### Findings

- [x] **ACC1 — MEDIUM — accuracy / one-rule-one-home** — `.agents/dotnet/contract/domain/values/SKILL.md:25`
  "a required column" is offered as a boundary that rejects an invalid default, but a NOT NULL column rejects
  only `null`: a value-typed field's default (`Guid.Empty`, `0`) is stored without complaint, so the rule would
  keep such a wrapper a struct on a false guarantee. It is also persistence vocabulary in a contract declaring
  no application-stack prerequisite. Fix: drop "a required column" and keep the holding entity's constructor
  as the boundary.
  Fixed in `a2686f3`: the example is now only "such as the holding entity's constructor".

## Review pass — 2026-10-04 — incremental

**Candidate base:** `4517d01020130a109ad0959364575f97eb7a7154`
**Candidate head:** `a2686f33b2ab1e0e8e5d7a5fdc748b6af6fa5aa1`
**Candidate branch:** `Fix/IdempotencyHashAndValueStructs`
**Candidate scope:** `all`
**Candidate path-set:** `sha256:d18d377b3ab93db24d9491e78e788bdf0218ebfe95e5127dafa2d005f13c758a` `(2 paths)`
**Candidate bundle:** `C:\Users\TommySeery\source\repos\tj-agents\dotnet\.git\agent-workflow\runs\idemhash-docs-review-2\review\1048d9be05f78cc7579d1f1b872c225a2d7ebe4fc0686ccf4b6f8dcccf8301c5`
**Candidate bundle identity:** `sha256:9bdf736abfaeb9e67bbef6639144aef84732820a105be27d447835ee89f79157`
**Work-order path:** `reviews/Fix-IdempotencyHashAndValueStructs.md`
**Work-order mode:** `append`
**Native layer:** `code-review` skill (medium); parent verified ACC1 resolution
**Pass judgment:** `approved`

### Findings

No findings.

## Review pass — 2026-10-05 — incremental

**Candidate base:** `a2686f33b2ab1e0e8e5d7a5fdc748b6af6fa5aa1`
**Candidate head:** `a0ac736493407105e9a6ae357c8d80ed8ecf0646`
**Candidate branch:** `Fix/IdempotencyHashAndValueStructs`
**Candidate scope:** `all`
**Candidate path-set:** `sha256:d4234fc54d86876336802d5b4dd7e449da498e945256212bbbb6181bb2b0670a` `(6 paths)`
**Candidate bundle:** `C:\Users\TommySeery\source\repos\tj-agents\dotnet\.git\agent-workflow\runs\idemhash-docs-review-3\review\6cdb615627be78407f2357d445abafaff201695f0048b8aa5c83e3c0aa005c8e`
**Candidate bundle identity:** `sha256:7b5c1ded4d7b1160f78530cd0227d33add400feb587eebb79cd69511b7525508`
**Work-order path:** `reviews/Fix-IdempotencyHashAndValueStructs.md`
**Work-order mode:** `append`
**Native layer:** `code-review` skill (medium); lens: accuracy+contradiction+home+concision+followability; docs reachability 0 errors
**Pass judgment:** `approved`

### Findings

No findings. (Native layer's "Evidence and Proof were distinct roles" dropped: it contests the owner's decision that they are near-synonyms, and leaving a trusted-without-recheck token unnamed was the chosen option over keeping `Proof`.)
