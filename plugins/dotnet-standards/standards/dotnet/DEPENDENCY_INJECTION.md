# Dependency injection

## Inject interfaces; register them in the owning composition root

Injected collaborators default to interface-typed dependencies and interface-to-implementation
registrations. Use a concrete type only where an interface adds literally no value or actively makes an
established pattern worse.

- **Your own services:** register the interface and its implementation in the owning module's or
  library's composition-root extension, and use constructor injection. Do not reach for
  `IServiceProvider` or a factory lambda for an ordinary dependency graph — a lambda that news up a
  graph by hand is service location wearing a registration's clothes.
- **Third-party SDKs:** use the vendor's own DI extension or root client where one exists; otherwise
  register only the service types actually consumed. Keep the SDK behind an infrastructure adapter, and
  never rebuild the vendor's service graph out of `IServiceProvider` factory lambdas.

Runtime resolution by key is confined to one place — see the `keyed-strategies` skill. Application
handlers, steps, services, and named facades never inject a service provider or call
`GetRequiredKeyedService`.

## A dependency-holder surfaces its dependencies as get-only auto-properties

When a type's whole job is to **surface its injected dependencies as public members** of an interface it
implements — it holds them and adds no behaviour of its own — assign the constructor parameters straight
to public get-only auto-properties. A private backing field mirrored by an expression-bodied property is
two members and a pointless double-hop for one dependency.

```csharp
internal sealed class StandardFulfilmentFlow : IFulfilmentFlow
{
    public StandardFulfilmentFlow(
        ReserveStockStep reserve,
        ChargeCardStep charge,
        DispatchStep dispatch)
    {
        this.Reserve = reserve;      // concrete parameter (what DI resolves) → interface-typed property
        this.Charge = charge;
        this.Dispatch = dispatch;
    }

    public IReserveStep Reserve { get; }
    public IChargeStep Charge { get; }
    public IDispatchStep Dispatch { get; }
}
```

The parameters stay **concrete** so DI resolves the registered concrete step, while the properties are
**interface-typed** — the contract consumers see. The implicit conversion happens at assignment, and the
assignments are `this.`-qualified like any other constructor assignment.

**This is not a licence to drop `private readonly` fields elsewhere.** It applies only where the member is
a genuine public part of the type's contract that passes the dependency straight through. A dependency the
type consumes *internally* — a repository a service queries, a client a step invokes — stays a
`private readonly` field, which is captured state and still governed by the `csharp-style` rule against
primary-constructor captures.

## Lifetimes

A component that resolves other components must not outlive them. A singleton that captures a scoped
dependency pins it for the process lifetime, and a facade that captures a scoped resolver must itself be
scoped. Where a stateful singleton legitimately captures a typed HTTP client, treat the pinned message
handler as a deliberate, documented trade-off — never the default shape for a hot or DNS-volatile client.
