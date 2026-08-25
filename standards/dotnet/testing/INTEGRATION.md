# Integration tests

An integration test boots the service's **real `Program`** through `WebApplicationFactory<Program>`
(`Microsoft.AspNetCore.Mvc.Testing`) and exercises it over HTTP against a real database. For pure in-memory
tests see `unit-testing`; for browser scenarios see `e2e-scenarios`.

`WebApplicationFactory<Program>` is also the mechanical line between the two tiers: a project that references
it is an integration test project, whatever its name says.

## Structure

Each service owns an `<Service>.IntegrationTests.Fixtures` project holding its `ApiFixture`, which derives from
`WebApplicationFactory<Program>` to boot that service's real `Program`. The fixtures are named identically per
service but live in their own namespaces, so a test project imports only its own.

The service-agnostic pieces live in a shared testing library referenced by every fixture: the SQL container plus
database-reset fixture, the test auth handler, the shared mocks, and the setup extensions.

- **Containerized database.** A fresh SQL container starts per test run via **Testcontainers**, and **Respawn**
  clears data between tests without re-running migrations. Naming the libraries is deliberate: "a container and
  a reset tool" is not something a reader can act on, and neither library is product-specific.
- **Authentication** through a test scheme registered as the default, driven by request headers carrying the
  subject and optional email. No token, and no role claim unless the test says so.
- **Webhook simulation** dispatches provider events directly to the registered handlers in a new scope, bypassing
  HTTP entirely.

## Anything shared by two fixtures belongs in the shared library

A fixture must never re-hand-roll setup another service already has. Anything common to two or more suites goes
in the shared testing library and is composed through extension methods and constants — never copy-pasted per
fixture. **When you catch yourself copying a setup step into a second fixture, lift it instead.** Typical
members of that library:

- environment names and checks as **extension members** hung onto `Environments` and `IHostEnvironment` —
  never a raw environment string literal;
- an `AddTestAuthentication()` that makes the test handler the default scheme;
- a logging extension that routes host logs to the current test's output;
- an extension that removes the real bus transport and swaps in a no-op, omitted in a service with no bus;
- a shared database initializer that migrates messaging tables, then migrates and runs every registered test
  seeder.

Only genuinely service-specific wiring — an identity provider's UI stack, an in-process dependency, provider
fakes, per-service mocks and seeders — stays in the service's own fixture.

Seeding rules, including the factory `Seed` pattern and the sentinel guard, are in the `seeding` skill and apply
to test seeders too.

## Adding a test

1. Create the class in the relevant module's integration-test project.
2. Annotate it with the shared `[Collection]` and inject the fixture through the constructor.
3. Reset the database in `InitializeAsync()`, not in the constructor — xUnit runs the constructor before the
   async lifetime hook, so a reset written there runs at the wrong time and silently leaves prior data in
   place.
4. Get an authenticated client from the fixture rather than building one.

Derive expectations from the canonical seed catalog the fixture exposes, never from invented literals.

## Scoped services and event handlers

An integration test is a scope root. Resolve an `IScoped<T>` abstraction from the fixture's services and use its
`RunAsync` whenever the test needs one scoped `DbContext`, repository, service, or handler collection. **Do not
hand-write `CreateScope()`/`CreateAsyncScope()` for those cases** — a manual scope is reserved for a test that
must coordinate several distinct services in one scoped lifetime with no narrower scope-root aggregate available.

Dispatch integration events through `IScoped<IEnumerable<IIntegrationEventHandler<TEvent>>>` and invoke every
registered handler **inside that one scope**, matching the in-process message pipeline.

**Do not use `IScoped<T>` from code already running inside a request or fixture-provided scope.** Resolve the
dependency from the ambient scope instead, so its `DbContext` and transaction stay shared.

## Group tests by the public resource being exercised

A service or module integration project is organized by the **public resource its API exposes**. Every
operation on one resource lives in one `<Resource><Qualifier>ApiTests` class — resource or controller first,
then any qualifier, then the fixed `ApiTests` suffix, which is never dropped. A courier slice of the Shipment
controller is `ShipmentCourierApiTests`, never `CourierShipmentApiTests`. `Api` rather than `Endpoints` or
`Controller`, because these drive the real HTTP surface through the Api assembly, not a controller class in
isolation.

Once a resource carries a substantial set of operations, group them with a `#region` per operation — `#region
Get`, `#region Create`, `#region Accept` — or per behaviour cluster where that is not a single operation
(`#region Cancel from payment failure`). Group with `#region`, **never** `// ---- X ----` dividers.

**A new class needs a reason of its own.** One operation currently having a single test is not one: it goes in
its resource's class under its own region, and that class absorbs the next operation without a rename. Split
only where the new class is a genuinely distinct **resource**, a distinct **public boundary**, a distinct
**fixture**, or one **coherent process** worth reading end to end. A class per variant — per deal type, per
status, per request shape — scatters one resource's contract across a directory and hides which operations are
covered at all.

```csharp
[Collection(IntegrationCollection.Name)]
public sealed class ShipmentApiTests(ShipmentApiFixture fixture)
{
    #region Get

    [Fact]
    public async Task Get_ReturnsOnlyTheOwningTenantsShipments()
    {
        var client = fixture.CreateClient(fixture.SeedState.WarehouseManager);

        var response = await client.GetAsync("/api/shipments");

        await response.ShouldBe(HttpStatusCode.OK);
        var shipments = await response.Content.ReadAsync<IReadOnlyList<ShipmentSummary>>();
        Assert.Contains(shipments!, item => item.Id == fixture.SeedState.PendingShipment.Id);
        Assert.All(shipments, item => Assert.Equal(fixture.SeedState.Warehouse.TenantId, item.TenantId));
    }

    #endregion

    #region Dispatch

    [Fact]
    public async Task Dispatch_MarksTheShipmentDispatchedAndQueuesTheCourierHandover()
    {
        var shipment = fixture.SeedState.PendingShipment;
        var client = fixture.CreateClient(fixture.SeedState.WarehouseManager);

        var response = await client.PostAsync($"/api/shipments/{shipment.Id}/dispatch", null);

        await response.ShouldBe(HttpStatusCode.OK);
        var dispatched = await fixture.Scoped<IShipmentReadDbContext>()
            .RunAsync(db => db.Shipments.SingleAsync(item => item.Id == shipment.Id));
        Assert.Equal(ShipmentStatus.Dispatched, dispatched.Status);
        Assert.Single(fixture.CourierHandovers, handover => handover.ShipmentId == shipment.Id);
    }

    #endregion
}
```

## Each endpoint test proves its own contract

Every test owns a real scenario for one operation: arrange the state or dependency response that matters, call
the endpoint, and assert the observable result — the returned contract, the persisted effect, the published
event. A successful status is one assertion inside that, never the whole test. Share setup and assertion
helpers wherever that removes repetition without hiding the scenario.

**A parameterized "these routes all return OK" test is not endpoint coverage.** It proves routing and
authorization wiring and nothing about behaviour, while reading as though the endpoints are covered. Keep
such a sweep — if at all — as one explicitly-named smoke test beside the real per-operation tests, never in
place of them.

## A module test stays at its owning public boundary

A module integration test drives that module's own public API and asserts only what the module owns: its
returned contract, its own persistence, the events it publishes. Reading a seeded identity off the shared seed
state to address its own API is not a boundary crossing; querying another module's `DbContext`, or invoking
another module's domain behaviour to arrange or assert, is.

**A journey that crosses modules belongs in the process integration tier** — its own suite, driving the real
host and observing each module through HTTP or a deliberate Contracts surface, referencing no module's Domain
or Infrastructure assembly. Pushing a cross-module journey down into one module's suite is exactly what forces
that suite to reach into persistence it does not own.

## A fixture helper stays fixture infrastructure

A helper that forces a deterministic failure, takes or holds a lock, or manipulates state that exists only for
a test **belongs to the fixture project**. It is never added as a member on a production `DbContext`,
repository or service: production then carries an API no production caller has, and the compiler can no longer
tell the two apart.
