# Code review — Refactor/OneTestingStyleStandard

**Review status:** `complete`
**Reviewed up to commit:** `9a62dbd4750f22fbd3e6586f2f4ed1bad2d57026`  `(2026-10-13)`
**Judgment:** `approved`

## Review pass 1 — 2026-10-13 — full, at `af2e298`

Independent review lens, scoped to cross-contract consistency, scaffold gates and routing.

- [x] P1: the style contract's "`this.` on every constructor assignment" conflicted with
  `dotnet_style_qualification_for_field = false:error`. Tommy decided Option A (only where a parameter
  shadows the field), and it's implemented in `2c8b7a9`.
- [x] P1/P2: `false:error` was inert without `EnforceCodeStyleInBuild`. Added in `2c8b7a9`. IDE0003 still
  never fires at build on SDK 10.0.301; I reproduced that independently, and `dotnet:style` states it as a
  partial gate.
- [x] P2: the E2E tier's Shouldly conflicted with Playwright's retrying assertions. Tommy decided the split
  (Playwright `Expect` for page state, Shouldly for off-page values), in `2c8b7a9`.
- [x] P2: `*Handler.cs` routed to `microservice-boundaries`. The processor and handler rows were split in
  `3d8276d`.
- [x] P2: the gates had no negative-path test. verify.py now asserts that a stray `Assert.*` fails the
  build (`2c8b7a9`), with a Python 3.9-compatible write in `1952e91`.

## Review pass 2 — 2026-10-13 — full, at `2c8b7a9`, every snippet against its host contract

Added after M003: the user caught the e2e example breaking its own contract, which pass 1 didn't check.
Every fenced block in the 13 touched contracts was checked against every rule of its host contract and the
cross-cutting contracts. No P1 or P2 findings: all snippets PASS, the decisions trace to GOAL.md, and
`dotnet:style` doesn't overclaim the IDE0003 gate.

- [x] P3: the elision comment in keyed/strategies' registration snippet predates this branch (it's on
  main). Left as is.

`1952e91` (the verify.py byte writes for Python 3.9) and `9a62dbd` (GOAL.md next steps) were reviewed by
the coordinator. CI is green on
`1952e91`: both scaffold verify configurations on ubuntu and windows, plus kit verify.
