# Unit tests

A unit test is a pure in-memory test of domain or service logic with **no** database, host factory,
containers, fixtures, or HTTP. If a test needs any of those, it is an integration test — see the
`integration-testing` skill.

General C# style — field naming, `this.` qualification, no primary-constructor captures — applies here
exactly as in production code.

## Framework and shape

- **xUnit.** `[Fact]` for a single case; `[Theory]` with `[InlineData(...)]` for tabular cases, keeping the
  expected value as the **last** argument.
- The test class is `public sealed class XTests`, in the test project's root namespace.
- **Arrange / Act / Assert separated by blank lines, with no `// Arrange` comments** — the blank lines carry it.

```csharp
public sealed class VatPolicyTests
{
    private readonly IVatPolicy policy;

    public VatPolicyTests()
    {
        this.policy = new VatPolicy(new UkVatCalculator());
    }

    [Theory]
    [InlineData(null)]
    [InlineData("")]
    public void Apply_UnregisteredSupplier_ReturnsNone(string? supplierVatNumber)
    {
        var result = policy.Apply(120m, supplierVatNumber);

        Assert.Equal(120m, result.Net);
    }
}
```

## Naming

`Method_Scenario_ExpectedBehaviour` — `Apply_RegisteredSupplier_DecomposesInclusiveGross`,
`Create_RateOutsideRange_ThrowsDomainException`. The scenario segment names the input state; the last segment
names the observable outcome. A terser `Method_ShouldXxx` form in older tests is legacy, not a second style to
choose from.

## SUT construction

- A SUT with dependencies is built **in the test-class constructor** and held as a `this.`-qualified
  `private readonly` field.
- **Prefer real collaborators over mocks** where they are cheap and deterministic — `new VatPolicy(new
  UkVatCalculator())`, not a mocked calculator. Reach for a test double only at a genuine boundary: I/O, time,
  randomness, or an expensive/nondeterministic dependency.

## Assertions

Pick **one** assertion library per test tier and use it consistently. Mixing two inside a tier means two failure
message formats and two idioms for the same assertion, for no benefit.

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
