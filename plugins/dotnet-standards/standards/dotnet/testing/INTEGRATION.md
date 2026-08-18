# Integration tests

An integration test boots the service's **real `Program`** and exercises it over HTTP against a real database.
For pure in-memory tests see `unit-testing`; for browser scenarios see `e2e-scenarios`.

## Structure

Each service owns an `<Service>.IntegrationTests.Fixtures` project holding its `ApiFixture`, which boots that
service's real `Program`. The fixtures are named identically per service but live in their own namespaces, so a
test project imports only its own.

The service-agnostic pieces live in a shared testing library referenced by every fixture: the SQL container plus
database-reset fixture, the test auth handler, the shared mocks, and the setup extensions.

- **Containerized database.** A fresh database container starts per test run; a reset tool clears data between
  tests without re-running migrations.
- **Authentication** through a test scheme registered as the default, driven by request headers carrying the
  subject and optional email. No token, and no role claim unless the test says so.
- **Webhook simulation** dispatches provider events directly to the registered handlers in a new scope, bypassing
  HTTP entirely.

## Anything shared by two fixtures belongs in the shared library

A fixture must never re-hand-roll setup another service already has. Anything common to two or more suites goes
in the shared testing library and is composed through extension methods and constants — never copy-pasted per
fixture. **When you catch yourself copying a setup step into a second fixture, lift it instead.** Typical
members of that library:

- environment names and checks as **extension members** hung onto the framework's own environment types — never
  a raw environment string literal;
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
2. Annotate it with the shared test collection and inject the fixture through the constructor.
3. Reset the database in the test's initialization step.
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

## Naming and grouping

**Naming.** Test files are `<Resource><Qualifier>ApiTests` — the resource or controller first, then any
qualifier, then the fixed `ApiTests` suffix. The suffix is never dropped and the resource always leads, so a
courier slice of the Shipment controller is `ShipmentCourierApiTests`, never `CourierShipmentApiTests`. `Api` rather
than `Endpoints` or `Controller`, because these drive the real HTTP surface through the Api assembly, not a
controller class in isolation.

**Regions handle one axis of variation; a file split handles the second.** Most controllers vary on a single
axis — their endpoints — so they get one file with a `#region` per endpoint, named for the endpoint under test,
or for the behaviour where a cluster is not a single endpoint (`#region Cancel from payment failure`). Group with
`#region` — **never** `// ---- X ----` comment dividers.

A controller that varies on **two** axes is a matrix, and a single regioned file cannot express it: one axis
becomes regions and the other becomes repeated sub-blocks inside every region. For that shape:

- **Primary axis → file split.** Split on the axis where behaviour genuinely forks — typically a lifecycle
  discriminator, one file per value. The qualifier in the file name *is* the primary-axis value.
- **Secondary axis → `#region`s inside each file.**
- **Cross-cutting behaviour belonging to no single value → its own file**, rather than duplicated across every
  value's file.

Regioning is for navigation, not a licence to sprawl.
