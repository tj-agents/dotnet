# E2E scenario authoring

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
`agent-process` standards rather than debugging application code.
