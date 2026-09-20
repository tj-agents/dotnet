---
name: e2e-scenarios
description: Authoring rules for browser E2E scenarios (Gherkin bound with Reqnroll, driven through Playwright) — a scenario tests one behaviour and starts at the nearest already-verified state, fast-forwarding through seeded data rather than replaying earlier stages through the UI, creating a prerequisite through its real production API or handler where seeding rules forbid seeding that row, splitting a scenario whose assertion needs genuine external-provider state, keeping a trusted baseline file's scenario lists and counts reconciled, and running headless by default. Use when writing or reviewing a UI E2E scenario, adding setup steps to reach a starting state, or reconciling a suite's pass/fail baseline.
kind: contract
domain: dotnet
profile: e2e
applicability: browser end-to-end suites using Gherkin and Playwright
requires: reqnroll, playwright
provenance: library, house
---

# E2E scenario authoring

## Applicability

This contract applies only to browser end-to-end suites using Gherkin and Playwright. It requires `reqnroll, playwright`. Installing `dotnet@dotagents` makes this guidance available; it does not select those technologies for a consuming repository.

Gherkin feature files bound to step definitions with **Reqnroll**, driving the browser through
**Playwright**. These rules are the same for every UI suite in a solution, so they live in one place; a
suite adds only its own fast-forward mechanics (the shape of its seed state).

## One behaviour, starting at the nearest already-verified state

**A scenario never re-drives earlier stages through the browser to reach its starting line.** If a happy path
already covers `create → book`, a scenario acting on a booking fast-forwards to "booked" and drives only its own
behaviour and assertion.

The litmus test before writing a setup `When`/`And`: *is this proving the behaviour in the scenario title, or
just getting me to the starting line?* If it is the latter and another scenario already covers it, make it a
fast-forward `Given`, not UI steps.

## Fast-forward without UI replay

By default a setup `Given` reads pre-seeded data off the suite's fixture and puts the id on scenario state — no
navigation, no clicks. Where the starting state does not exist yet, add the seeded state plus a `Given`.

Where the `seeding` rules forbid seeding that lifecycle row — an invitation, say — create the prerequisite
through its **real production API or handler** from a non-UI `Given`. Never replay browser UI to build setup, and
never insert the row directly.

## The one thing you cannot seed: real external-provider state

Seeding obeys production's rule that a seeder writes only what production writes directly, and a payment provider
emits only on live webhooks — so no seeder creates a real charge. A scenario whose assertion needs a genuine
provider object (a refund reversing a real charge) must run the real paying flow and cannot be pure-seed
fast-forwarded. **Split it:** the cheap state-transition assertion starts from seeded state, and the
provider-dependent assertion stays on a flow that actually paid.

## Baseline discipline

Where the suite trusts a checked-in baseline of passing and failing scenarios, two traps recur:

1. When a scenario crosses the line, move it between the passing and failing blocks **and** fix both counts and
   the summary table — the parser fails on a mismatch.
2. Adding an assertion to an already-green scenario can silently turn it red while the baseline still lists it as
   passing: the name did not change, but the body now fails. **A name in the passing list is not proof the
   current body passes** — re-run and reconcile.

## Headless by default

Playwright runs headless; headed mode changes nothing that is asserted, so use it only when a human is
watching. Before rerunning a suite that
died at fixture startup, treat it as an environment problem — see the container-health rule in the
`engineering` standards rather than debugging application code.

## Another service's state is read through that service's own Db class

A suite never inlines a SQL string against another service's tables — not in a fixture, and least of all in
the shared harness, which is service-agnostic and has to move the moment it names one service's table. The
read belongs in a small `XDb` class in that service's E2E helpers, and the suite depends on it explicitly.

## A readiness gate asserts what the tests consume, and re-asserts after a reset

Counting rows proves nothing. The count can be satisfied by records the tests never touch, and a row can
exist while the half a test needs is still absent — a payout owner with its payee account provisioned but
not yet its payer side reads as "ready" and then fails the first charge. Gate on the **identities the suite
transacts as** and on every field it depends on.

Whether the gate belongs after a reset too is decided by one thing: whether the resetter clears those rows.
A resetter that excludes the provisioning tables leaves them intact, so a post-reset gate polls for a
condition already true; one that truncates them re-drives the registration chain, and the first test after
each reset races that window. Check the resetter's exclusion list rather than assuming either.

Either way the gate at boot is not optional. Without it the suite fails its first test and succeeds on the
same call later — which reads as flakiness and is not.
