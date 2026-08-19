---
name: e2e-scenarios
description: Authoring rules for browser E2E scenarios (Gherkin bound with Reqnroll, driven through Playwright) — a scenario tests one behaviour and starts at the nearest already-verified state, fast-forwarding through seeded data rather than replaying earlier stages through the UI, creating a prerequisite through its real production API or handler where seeding rules forbid seeding that row, splitting a scenario whose assertion needs genuine external-provider state, keeping a trusted baseline file's scenario lists and counts reconciled, and running headless by default. Use when writing or reviewing a UI E2E scenario, adding setup steps to reach a starting state, or reconciling a suite's pass/fail baseline.
---

# e2e-scenarios

The standard is `../../standards/dotnet/testing/E2E.md`, shipped in this plugin. Read it and follow it; this skill only routes to it.
