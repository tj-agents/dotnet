---
name: testing-unit
description: Unit-test standard for .NET — integration is the default for application services, handlers, controllers, repositories, DI, adapters and collaborator orchestration; unit tests are reserved for substantial deterministic core logic such as calculations, validators, decision tables, value objects and domain transitions, never mock-interaction coverage of guard clauses or delegation. Also owns xUnit shape, constructor-built SUTs, real collaborators and self-verifying architecture allowlists; test naming and the assertion library are owned by `dotnet:testing`. Use when adding or reviewing a test or deciding between the unit and integration tiers.
kind: contract
domain: dotnet
profile: unit-testing
applicability: projects using xUnit for deterministic core logic
requires: xunit
provenance: library, house
---

# Unit tests

Owns when a test belongs at the unit tier, plus xUnit shape and SUT construction. Naming and the
assertion library are owned by `dotnet:testing`.

## Applicability

This contract applies only to projects using xUnit for deterministic core logic. It requires `xunit`. Installing `dotnet@tj-agents` makes this guidance available; it does not select those technologies for a consuming repository.

```csharp
public sealed class InventoryTests
{
    private readonly Inventory inventory;

    public InventoryTests()
    {
        inventory = new Inventory(new StockCatalog());
    }

    #region Receive

    [Theory]
    [InlineData(5, 3, 8)]
    [InlineData(0, 4, 4)]
    public void Receive_PositiveQuantity_IncreasesStock(int initialStock, int quantity, int expected)
    {
        inventory.Receive("sku-1", initialStock);

        inventory.Receive("sku-1", quantity);

        Assert.Equal(expected, inventory.StockOf("sku-1"));
    }

    #endregion
}
```

`InventoryTests` is the whole standard in one place: `Method_Scenario_ExpectedBehaviour` naming, a
constructor-built `private readonly` field, Arrange/Act/Assert separated by blank lines, xUnit's
`Assert.*`, a `[Theory]` with the expected value last, and a `#region` per method under test. Its parameterless constructor assigns `inventory` unqualified —
per `dotnet:fields`, `this.` appears only where a constructor parameter shadows the field it
fills, and nothing here does.

A unit test is a pure in-memory test of substantial, deterministic core logic with **no** database, HTTP,
fixtures, or `WebApplicationFactory`/`TestServer` host, and no `Testcontainers` container. Good candidates
are calculations, transformations, validators, decision tables, value objects, and domain state transitions
whose cases are clearer when exercised directly. If a test needs infrastructure, it is an integration test
— see the `testing-integration` skill.

Those type names are the point, not decoration: they are what a reader greps for and what a build gate can
match on. "A host factory" cannot be enforced by anything.

## Integration is the default

Default to an integration test for application services, handlers, controllers, repositories, dependency
injection, adapters, and behaviour that coordinates collaborators. Those types exist to connect real
boundaries; replacing every boundary with a mock proves the test's setup rather than the application.

Do not add a unit test merely to cover a guard clause, a delegation path, or whether a collaborator was or
was not called. A test whose main assertion is mock interaction is normally an integration test expressed
at the nearest real application boundary. Use a unit test only when the isolated logic itself has enough
meaningful cases to justify direct coverage and an integration test would obscure that logic. If in doubt,
write the integration test.

Code being private, internal, or inconvenient to reach is not by itself a reason for a unit test. Test
through the public behaviour unless direct coverage materially improves the clarity or completeness of the
core logic's cases.

`dotnet:fields` — field naming, `this.` qualification, no primary-constructor captures — applies here
exactly as in production code.

## Framework and shape

- **xUnit.** `[Fact]` for a single case; `[Theory]` with `[InlineData(...)]` for tabular cases, keeping the
  expected value as the **last** argument.
- The test class is `public sealed class XTests`, in the test project's root namespace.
- **Arrange / Act / Assert separated by blank lines, with no `// Arrange` comments** — the blank lines carry it.

## Naming and assertions

Test naming (`Method_Scenario_ExpectedBehaviour`) and the per-tier assertion library are owned by
`dotnet:testing`; this tier's library is xUnit's `Assert.*`.

## SUT construction

### Test constructor

xUnit creates a fresh test-class instance for every test, so the constructor is the per-test reset boundary.
As in the `InventoryTests` example above, declare mocks, collaborators, and the SUT as `private readonly`
fields without initializers. Construct each dependency explicitly in the constructor, then construct the SUT
from those fields.

- **Never a per-test `CreateSut()`/`CreateService()` factory method.** A private method rebuilt on every
  call is the constructor's job wearing a disguise — it buys nothing the constructor doesn't already give
  every test, and it's the tell that mocks are being re-declared as local variables per test instead of
  living as constructor-built fields. If you're about to write one, put its body in the constructor
  instead and reference the fields directly.
- **Prefer real collaborators over mocks** where they are cheap and deterministic — `new Inventory(new
  StockCatalog())`, not a mocked catalog. Reach for a test double only at a genuine boundary: I/O, time,
  randomness, or an expensive/nondeterministic dependency, and only when the SUT still owns substantial
  isolated logic. Several mocked collaborators are a strong signal that the test belongs in the integration
  tier.

## Grouping a large test class

Where one class covers several methods of a SUT, divide it into `#region`s named for the **method under test**
(`#region Apply`, `#region Create`); a cluster that is not a single method names the behaviour instead
(`#region Late capture compensation`). Regioning is for navigation, **not** a licence to sprawl — when a class
outgrows comfortable regioning, split it by SUT method into separate files rather than piling on more regions.

## An architecture-guard allowlist must verify itself

A repo-wide guard — an architecture test that scans every source file — sometimes needs a temporary allowlist for
files mid-migration. Express the allowlist as a **`public static TheoryData<>`** feeding a self-verifying
`[Theory]` that asserts each allowlisted item **still violates** the rule, so a stale entry fails the theory and
forces its own removal. The guard `[Fact]` excludes that same `TheoryData` — one source of truth. Never a
silently-suppressing exclusion list, which rots the moment the first item is fixed.
