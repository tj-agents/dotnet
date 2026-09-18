# Domain events — raised in the domain, dispatched by the save, published as integration events

A domain method that changes state never calls a bus, a notifier, or another module. It **raises** a
domain event on the entity; the persistence layer dispatches it when the change is saved. Two things
follow that are the whole point of the pattern: the domain project takes no infrastructure dependency,
and a caller cannot forget to publish, because publishing is no longer the caller's job.

## An entity composes an event collection — it does not inherit an aggregate base

The entity implements a two-member raiser contract — the read-only event list, and a clear — by holding
a private collection object and calling `Raise(...)` from its own methods. Composition, not a base
class: an entity is then free to inherit whatever its persistence layer needs, and a mapped read model
that raises nothing simply does not implement the contract.

```csharp
public sealed class OrderEntity : IEventRaiser
{
    private readonly EventRaiser events = new();

    public IReadOnlyList<IDomainEvent> DomainEvents => events.DomainEvents;
    public void ClearDomainEvents() => events.Clear();

    public void Cancel(string reason)
    {
        Status = OrderStatus.Cancelled;
        events.Raise(new OrderCancelledDomainEvent(this));
    }
}
```

A domain event is a `sealed record` implementing the marker interface, named past-tense with a
`DomainEvent` suffix, and lives in the **domain** project beside the entity that raises it.

## The save is what dispatches, in two phases

A `SaveChangesInterceptor` collects the events off every tracked raiser, clears them, and dispatches:

- **Pre-commit**, inside `SavingChangesAsync` — the handler's own writes join the caller's transaction
  and commit atomically with it.
- **Post-commit**, inside `SavedChangesAsync` — for work that must not run unless the change actually
  committed, and whose own failure must not roll the change back.

Clearing before dispatch is load-bearing: a handler that saves again re-enters the interceptor, and an
uncleared collection dispatches the same event a second time.

**Pre-commit is the default.** Reach for post-commit only when the side effect is genuinely
non-transactional, and never for a bus publish that goes through an outbox — the outbox row is the
thing that must be atomic.

## A pre-commit handler is where a domain event becomes an integration event

The domain event is internal to the service and carries the entity. The integration event is the
published contract and carries a flat payload. One pre-commit handler per domain event does the
translation and nothing else:

```csharp
internal sealed class OrderCancelledDomainEventHandler : IPreCommitDomainEventHandler<OrderCancelledDomainEvent>
{
    public Task HandleAsync(OrderCancelledDomainEvent e, CancellationToken ct = default) =>
        bus.PublishAsync(new OrderCancelledEvent(e.Order.Id, e.Order.CustomerId, e.Order.CancelledAt), ct);
}
```

Because the bus is a transactional outbox, that publish stages a row on the caller's context — so the
state change and the promise to tell the world commit or roll back together. Publishing after the
commit instead is the classic lost-message bug.

**Never let a domain event cross a service boundary.** It is a type in the domain project, holding a
live entity; the thing another service subscribes to is the integration event.

## Handlers are registered per closed event type

The dispatcher resolves `IDomainEventHandler<TEvent>` for the runtime type of each event, so every
handler is registered against its closed interface in the owning module's DI extension. A handler
registered only as its concrete class is never found, and the failure is silent — the event dispatches
to nothing.

```csharp
services.AddScoped<IDomainEventHandler<OrderCancelledDomainEvent>, OrderCancelledDomainEventHandler>();
```

Zero handlers for an event is valid. More than one is valid, and they run in registration order within
their phase.

## Anti-patterns

- **Publishing an integration event from an application service or handler**, in parallel with the
  write. Two independent operations, no shared transaction — the write commits and the message is lost,
  or the message goes out for a write that rolled back.
- **Injecting a bus, mailer or HTTP client into the domain project** so the entity can announce itself.
  That is the dependency this pattern exists to remove.
- **A handler that does business work.** A pre-commit handler translates and forwards. A handler that
  decides something is a domain rule sitting in infrastructure, where no domain test reaches it.
- **Raising from a property setter or a mapper.** Events belong to intent-named domain methods; a
  setter cannot say what happened.
