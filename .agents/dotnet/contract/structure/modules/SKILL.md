---
name: structure-modules
description: How a module or shared library inside a .NET service is laid out — the Contracts/Domain/Application/Infrastructure/Api layer split with its inward-only reference graph, which layers a given component actually needs, where the clock is resolved and how the current instant reaches a domain method, the visibility cascade (public contracts, internal domain/application/infrastructure, `InternalsVisibleTo` for siblings and tests), project and folder naming, and the cross-module rules — no cross-module queries even from a read stance, communication only through a module facade or an integration event, primitive foreign keys across boundaries, shared reference vocabulary as an enum rather than a table, and facades that adapt an application use case instead of reimplementing one. Use when creating a project, deciding which layer a type belongs in, promoting a type to public, wiring one module to another, or deciding where the current time is resolved.
kind: contract
domain: dotnet
profile: modular-services
applicability: modular service or layered shared-library architecture
requires: modular-service-architecture
provenance: architecture, house
---

# Module structure

Owns module/library layering, visibility, folder naming and cross-module rules.

## Applicability

This contract applies only to modular service or layered shared-library architecture. It requires `modular-service-architecture`. Installing `dotnet@dotagents` makes this guidance available; it does not select those technologies for a consuming repository.

Applies to **modules** (a unit of audience-facing functionality) and to **shared libraries** that are not tied
to one module's data. Same layering rules; the only difference is that a shared library is consumed by several
modules or services.

## Layers

Pick the layers the component needs — not every module has all five.

| Layer | Purpose | Visibility |
|---|---|---|
| `X.Contracts` | Cross-boundary surface: interfaces, events, marker types, value types other consumers see. | `public` |
| `X.Domain` | Entities, value objects, domain events. Pure types, no infrastructure dependencies. | `internal` |
| `X.Application` | Service and repository interfaces, validators, internal DTOs, mappers. | `internal` |
| `X.Infrastructure` | EF configurations, `DbContext`, concrete implementations, event handlers, DI registration. | `internal` |
| `X.Api` | Controllers and HTTP-specific extensions. **Modules only** — a shared library exposes no HTTP. | `internal` |

```text
Contracts       → Kernel (and other Contracts when sharing base types)
Domain          → Contracts, Kernel
Application     → Domain, Contracts, Kernel
Infrastructure  → Application, Domain, Contracts, Kernel, framework deps
Api             → Application, Contracts, Kernel, ASP.NET
```

**Arrows only point inward.** `Domain` never references `Infrastructure`; `Contracts` never references
`Application`.

When each layer is warranted:

- **Contracts** — the thing has a cross-boundary surface (a cross-module facade, cross-service events, public
  types). A purely internal helper has none.
- **Domain** — it owns entities, value objects, or domain events. A pure utility library has no domain.
- **Application** — there are abstractions distinct from their infrastructure implementations.
- **Infrastructure** — there are concrete implementations behind those abstractions, or it owns EF mappings.
- **Api** — it exposes HTTP endpoints.

## Time

`TimeProvider` is resolved in `Application` or `Infrastructure`, once per operation, and the instant passed
into domain methods as a value. An entity never holds a clock — EF materializes it and cannot inject one.
A `Domain`-declared `IClock` is warranted only when a domain service consumes it, implemented in
`Infrastructure` over `TimeProvider`; declared earlier it is a port in a layer that never calls it.

## Visibility cascade

- `*.Contracts` types are `public` — they *are* the cross-boundary contract.
- `*.Domain` entities default to `internal`. Promote to `public` **only** where another module legitimately
  needs the type, such as a cross-module read projection target.
- `*.Application` interfaces stay `internal`, with `InternalsVisibleTo` for the module's own Infrastructure and
  Api assemblies.
- `*.Infrastructure` implementations stay `internal`.
- `*.Api` controllers stay `internal` too. ASP.NET's default `ControllerFeatureProvider.IsController`
  requires a public type, so this needs a custom provider overriding `IsController` — without one the
  routes silently do not exist. Make a controller `public` only where something outside the assembly
  genuinely resolves the type.
- Tests reach internals through `InternalsVisibleTo` for the unit and integration test assemblies, declared on
  the owning project.

## Folder and project naming

A module's project names include the owning service segment; genuinely cross-service shared libraries are
unprefixed.

```text
<Service>/Modules/<Module>/
  <Product>.<Service>.<Module>.Contracts/
  <Product>.<Service>.<Module>.Domain/
  <Product>.<Service>.<Module>.Application/
  <Product>.<Service>.<Module>.Infrastructure/
  <Product>.<Service>.<Module>.Api/
  Tests/
    <Product>.<Service>.<Module>.UnitTests/
    <Product>.<Service>.<Module>.IntegrationTests/
```

Shared libraries follow the same per-layer split when they need more than one layer.

## File structure

The layout above is the tree `dotnet:scaffold` creates for a new module: one project folder per layer the
module needs, each named `<Product>.<Service>.<Module>.<Layer>`, plus a `Tests/` folder holding the
unit and integration test projects. A shared library takes the same per-layer folders without the
`<Service>` segment and without an `Api` project.

## Cross-module rules

- **Zero cross-module runtime queries.** Every module reads only from its own `DbContext`.
- **That applies per *stance* too.** Where a module has both a tenant-bound context and a tenant-independent
  read context, the read context still composes only *that module's* configuration provider. A service-wide
  context over every module's model is exactly the monolith query surface this rule exists to prevent — do not
  add one, not even for integration fixtures; each fixture reads back through the owning module's own context.
- **Cross-module communication is a facade or an event** — an `IXModule` facade in Contracts for commands and
  narrow queries, or an integration event for fan-out.
- **Cross-module foreign keys are plain primitives** (`int WarehouseId`, `Guid UserId`) — never a navigation
  property across a boundary.
- **Shared reference vocabulary is an enum in the shared contracts package**, not a table every module keys
  into. There is no shared reference `DbContext`.

## A module facade adapts a use case; it is not a second service

An `IXModule` implementation is a cross-module adapter. It depends on the owning module's application service
or a focused use-case interface and forwards the declared `Option` or `Result` **directly**.

- Do not inject repositories, mappers, or a `DbContext` into a facade.
- Do not duplicate mapping, validation, or typed-result reconstruction in it.
- Add the required operation to the cohesive `IXService` where it belongs; if that interface has grown too
  broad, introduce a focused query or command service instead.
- Where the cross-module contract needs different semantics, implement those semantics as an application use
  case and keep the facade as its adapter.
