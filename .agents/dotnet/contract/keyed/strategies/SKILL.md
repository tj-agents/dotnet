---
name: keyed-strategies
description: The standard shape for behaviour that varies by a closed key in a .NET service — one module-local generic factory owning keyed DI resolution, operation-specific named facades that delegate through it, a registration builder that declares every family vertically and rejects duplicate keys, incomplete coverage and conflicting lifetimes so adding an enum member fails composition, the type-hierarchy half for branches DI cannot reach (an ORM-materialised entity, where the persistence discriminator is the key), matching a shared concern as a capability rather than by the key, and the anti-patterns it replaces (branching on the key inside key-agnostic code, service location outside the factory, parallel hand-written maps, returning an enum every caller re-switches on, throwaway result records, discard-tuple calls). Its sibling is `keyed-unions`, for variants that do not share one signature. Use when behaviour differs per enum/discriminator value, when adding a value to such an enum, when tempted to write a `switch` on a type/kind/mode key, when the branch sits in an entity the container cannot reach, when a concern spans some keys but not all, or when reviewing keyed DI registrations.
kind: contract
domain: dotnet
profile: keyed-design
applicability: closed-key behaviour selected through keyed dependency injection
requires: microsoft-extensions-dependency-injection
provenance: framework, pattern, house
---

# Keyed strategies

Owns the shape for behaviour that varies by a closed key through keyed dependency injection.

## Applicability

This contract applies only to closed-key behaviour selected through keyed dependency injection. It requires `microsoft-extensions-dependency-injection`. Installing `dotnet@dotagents` makes this guidance available; it does not select those technologies for a consuming repository.

**When behaviour varies by a closed key**, declare every strategy family vertically at the owning module's
composition root. A module-local generic factory owns keyed resolution; operation-specific facades delegate
through it. Consumers never branch on the key, never see the registration mechanism, and never inject the
generic factory merely to perform a business operation.

**This document covers variants that share one identical interface.** Where the variants differ in parameters
or return type, the family is a union resolved by key, not a strategy — `dotnet:keyed-unions` owns that half.
Applying these rules to that shape is what produces implementations that discard parameters, marker-interface
arms, and parameter objects invented to force differently-shaped variants into one signature.

The factory's noun names **what it returns**. The key is only the selection input:

```csharp
internal interface IFulfilmentStrategyFactory<TStrategy>
    where TStrategy : class
{
    TStrategy Create(FulfilmentMode mode);
}

internal sealed class FulfilmentStrategyFactory<TStrategy> : IFulfilmentStrategyFactory<TStrategy>
    where TStrategy : class
{
    private readonly IKeyedServiceProvider services;

    public FulfilmentStrategyFactory(IKeyedServiceProvider services)
    {
        this.services = services;
    }

    public TStrategy Create(FulfilmentMode mode) =>
        services.GetRequiredKeyedService<TStrategy>(mode);
}
```

## The builder makes incomplete coverage a composition failure

Record registrations before mutating `IServiceCollection`, then reject duplicate keys, undeclared or
incomplete coverage, unexpected keys, and conflicting lifetimes. Every family declares `RequireAll<T>()` or
`RequireExactly<T>(...)`, so **adding an enum member fails composition until the new type is handled
deliberately** — which is the whole point: the alternative is a `GetRequiredKeyedService` that throws in
production for one key nobody remembered.

```csharp
services.AddFulfilmentStrategies(strategies =>
{
    strategies.For(FulfilmentMode.Courier)
        .AddSingleton<IFulfilmentMapper, CourierFulfilmentMapper>()
        .AddSingleton<IFulfilmentUpdater, CourierFulfilmentUpdater>();

    // The other modes follow in the same vertical block.

    strategies.RequireAll<IFulfilmentMapper>();
    strategies.RequireAll<IFulfilmentUpdater>();
});
```

## Rules of the shape

- **A factory returns a selected component; a resolver consumes one and returns the final domain answer.**
  Mappers, renderers, serializers, and calculators keep naming the operation they perform — sharing a
  selection mechanism never flattens those suffixes into `Strategy`.
- **Factories and keys are module-local; a key-generic builder may be shared from a service-internal
  library.** Two modules with different runtime concerns own separate factories and registration blocks. Do
  not create a cross-module registry or put the factory in a shared contracts package.
- **Only the factory implementation performs keyed lookup.** A composition root may register the scoped
  keyed-provider adapter; application handlers, steps, services, and named facades never inject it or call
  `GetRequiredKeyedService`.
- **The factory is scoped.** A selected leaf may depend on scoped repositories or clients. Stateless leaves
  may stay singleton, but any unkeyed facade that captures the factory must also be scoped.
- **Named facades remain the business API.** They implement their operation-specific interfaces and delegate
  selection to the module factory. A *named* factory stays a factory where its caller genuinely needs the
  selected instance itself.
- **One exhaustive match over a sealed hierarchy, at one call site, is not the anti-pattern.** The
  prohibition is on a branch *repeated* across agnostic components. A module boundary needs a carrier, and
  matching its arms once where that carrier is received is the boundary working.
- **Methods return existing domain types or scalars.** Do not mint a one-use DTO, and do not return an enum
  every caller must reinterpret; add a second operation-specific method when a caller needs another value.

## When the container cannot reach the branch, the type is the family

An entity is materialised by the ORM, not the container, so it can neither inject the factory nor be a keyed
leaf. There the **type hierarchy is the family** and the persistence discriminator is the key. Map TPH onto
the key column that already exists rather than adding a second one:

```csharp
builder.HasDiscriminator(fulfilment => fulfilment.Mode);
```

Each leaf then declares what the branch used to ask for, and there is nowhere left for a switch to live:

```csharp
public abstract class Fulfilment
{
    public abstract bool RequiresTracking { get; }
}

public sealed class CourierFulfilment : Fulfilment
{
    public string TrackingNumber { get; private set; } = null!;

    public override bool RequiresTracking => true;
}
```

One leaf per key, each holding only its own fields. **A leaf covering two keys still has to re-ask the key** —
that is the signal the hierarchy sits at the wrong granularity, and it is what the `_ => throw` arm of an
inexhaustive switch is really reporting. Columns meaningful for some keys and always null for the rest say
the same thing one layer down.

Never hoist a leaf's operation onto the base to make one signature fit. A leaf overriding with a discard
parameter means the leaves perform *different* operations; match once at the call site owning that
calculation instead.

## Match on capability, not on the key

Concerns partition a key differently: the values sharing a settlement rule are rarely the values sharing a
financial operation or a cancellation path. No single inheritance axis serves every partition, which is why
one coarse hierarchy leaves each consumer re-splitting by hand. Give the shared concern its own interface and
match on that. A `bool RequiresX` threaded through constructors is the same branch, hidden — the leaves that
set it *are* the capability. Earn each capability on a second real consumer, never on the partition table
alone.

## The anti-patterns this replaces — never do these

- **Branching on the key inside key-agnostic components.** A `mode == Courier ? … : …` ternary or switch in a
  handler, service, or mapper that is otherwise agnostic plants a business rule where nobody will look for
  it, and it *will* get copy-pasted — that is how it spreads. The rule lives in exactly one resolver.
- **Service location outside the factory.** `IKeyedServiceProvider` or `GetRequiredKeyedService<T>(key)` in a
  handler, step, service, or named facade leaks the dispatch mechanism into business code.
- **Parallel hand-written maps.** A `FrozenDictionary<TKey, …>` per facade duplicates the coverage
  declaration and lets one family drift when a new key is added. Declare all families in the validated
  builder instead. (A frozen map is right for closed key-to-**data** tables — see `dotnet:naming-mapping`.)
- **Enum plus switch as an API.** Returning a label every caller re-interprets with its own switch multiplies
  the branch across the codebase. Return the resolved *value*.
- **Throwaway result records.** A record created only to carry one resolver's return values is noise —
  prefer separate methods or an existing domain type.
- **Mirroring a family into a downstream module.** Copying per-key fields into a second parallel hierarchy
  duplicates the data instead of dispatching it. Where a value must survive later edits to its source,
  freeze it once on the type that owns the frozen fact and carry it onward as one payload.
- **A per-key literal in a base constructor call.** `: Base(..., true, ...)` written once per leaf is a
  switch spelled as N call sites, and it reaches storage as a column no reader can trust. Declare it as an
  overridden member on the leaf that knows the answer.
- **Discard-tuple calls.** `var (thing, _) = await GetPairAsync(...)` means the API is the wrong shape for the
  caller; add the single-value method to the interface.
