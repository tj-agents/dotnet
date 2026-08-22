# Unit tests

A unit test is a pure in-memory test of substantial, deterministic core logic with **no** database, HTTP,
fixtures, or `WebApplicationFactory`/`TestServer` host, and no `Testcontainers` container. Good candidates
are calculations, transformations, validators, decision tables, value objects, and domain state transitions
whose cases are clearer when exercised directly. If a test needs infrastructure, it is an integration test
— see the `integration-testing` skill.

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
    private readonly VatPolicy policy;

    public VatPolicyTests()
    {
        this.policy = new VatPolicy(new UkVatCalculator());
    }

    [Theory]
    [InlineData(null)]
    [InlineData("")]
    public void Apply_UnregisteredSupplier_ReturnsNone(string? supplierVatNumber)
    {
        var result = this.policy.Apply(120m, supplierVatNumber);

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

### Test constructor

xUnit creates a fresh test-class instance for every test, so the constructor is the per-test reset boundary.
As in the `VatPolicyTests` example above, declare mocks, collaborators, and the SUT as `private readonly`
fields without initializers. Construct each dependency explicitly in the constructor, then construct the SUT
from those fields.

- **Never a per-test `CreateSut()`/`CreateService()` factory method.** A private method rebuilt on every
  call is the constructor's job wearing a disguise — it buys nothing the constructor doesn't already give
  every test, and it's the tell that mocks are being re-declared as local variables per test instead of
  living as constructor-built `this.`-qualified fields. If you're about to write one, put its body in the
  constructor instead and reference the fields directly.
- **Prefer real collaborators over mocks** where they are cheap and deterministic — `new VatPolicy(new
  UkVatCalculator())`, not a mocked calculator. Reach for a test double only at a genuine boundary: I/O, time,
  randomness, or an expensive/nondeterministic dependency, and only when the SUT still owns substantial
  isolated logic. Several mocked collaborators are a strong signal that the test belongs in the integration
  tier.

## Assertions

Pick **one** assertion library per test tier and use it consistently. Mixing two inside a tier means two failure
message formats and two idioms for the same assertion, for no benefit.

The usual assignment: **unit tests use xUnit's built-in `Assert.*`** (`Assert.Equal`, `Assert.True`,
…), **integration tests use Shouldly `ShouldBe`**, whose failure message carries the URL, status and response
body — which is worth far more at that tier than at this one.

**Whichever assignment a repo picks, enforce it in the build rather than at review.** A per-tier assertion
library is exactly the kind of rule a reviewer stops noticing: gate it from the test project's tier so a
reference to the wrong library fails compilation, and the choice stops being re-litigated per PR.

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
