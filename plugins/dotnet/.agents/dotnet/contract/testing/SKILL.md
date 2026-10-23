---
name: testing
description: Tommy's agreed .NET testing — test tiers, their naming, layout and fixtures. Read before writing or reviewing .NET that touches it; nothing applies until it is recorded here.
kind: contract
domain: dotnet
profile: core
applicability: .NET projects
requires: dotnet
provenance: house
---

# .NET testing

Owns test naming and the per-tier assertion library for every test tier, plus layout and fixtures.

Tier-specific authoring rules live with their own skill: `dotnet:testing-unit`,
`dotnet:testing-integration`, `dotnet:testing-e2e`.

## Agreed

### Every tier names its tests the same way

```csharp
public void Add_TwoOperands_ReturnsTheirSum(int left, int right, int expected)
```

`Method_Scenario_ExpectedBehaviour` is the test-naming standard for unit, integration and e2e alike:
`Method` names the member (or, for a Gherkin scenario, the behaviour under test), `Scenario` the input
state, `ExpectedBehaviour` the observable outcome. 2026-10-13: one name shape, owned in one place, so
`dotnet:naming`, `testing-unit`, `testing-integration` and `testing-e2e` route here rather than each
keeping its own naming rule.

### Each tier owns one assertion library

| Tier | Library |
|---|---|
| Unit | xUnit `Assert.*` |
| Integration | Shouldly |
| E2E — page state | Playwright `Expect(locator)` (`Microsoft.Playwright.Assertions`) |
| E2E — a value read outside the page | Shouldly |

The table is the default; a test project already using another library keeps it under the tier gate's
codebase-conventions rule. 2026-10-23: a session added xUnit `Assert` to a FluentAssertions project.

2026-10-13: a tier mixing two assertion libraries produces two failure-message formats and two idioms
for the same check, for no benefit. Gate the choice in the build rather than at review. E2E is the one
exception, and it is a library split rather than a mix: `Expect` auto-retries until the page matches, so
a scenario checking what the browser renders never races the UI the way a one-shot
`TextContentAsync`-then-`ShouldBe` read would; Shouldly still owns a value the step reads from outside
the page, such as an API response used to seed or verify state.
