---
name: domain-events
description: Domain events in a .NET service — a domain method raises an event on the entity instead of calling a bus, the entity composes an event-raiser collection rather than inheriting an aggregate base, persistence dispatches through its selected save boundary, one pre-commit handler per event translating the domain event into the published integration event so the outbox row commits atomically with the state change, handlers registered against the closed IDomainEventHandler<TEvent> interface because a concrete-only registration dispatches to nothing silently, and the anti-patterns (publishing alongside the write, injecting a bus into the domain project, business logic in a handler, raising from a setter). Use when a state change must announce itself, adding or reviewing a domain event or its handler, deciding pre-commit versus post-commit, wiring an integration-event publish, or when a domain project is about to take an infrastructure dependency.
kind: contract
domain: dotnet
profile: domain-model
applicability: domain models raising and dispatching in-process events
requires: domain-events
provenance: library, architecture, house
---

# Domain events — raised in the domain, dispatched by the save, published as integration events

Owns how a domain event is raised, dispatched at save, and translated into a published integration event.

## Applicability

This contract applies to domain models raising and dispatching in-process events. It requires `domain-events`. Installing `dotnet@tj-agents` makes this guidance available; it does not select those technologies for a consuming repository.

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

    public OrderStatus Status { get; private set; }
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

## Persistence dispatch

Persistence dispatches the accumulated events at its selected save boundary. The persistence adapter
owns transaction enlistment and the timing of each phase. When EF Core is selected, `efcore:event-dispatch`
owns the interceptor, clearing, pre-commit and post-commit implementation. A post-save callback alone
does not prove an enclosing transaction has committed.

## A pre-commit handler is where a domain event becomes an integration event

```csharp
public sealed record OrderCancelledDomainEvent(OrderEntity Order) : IDomainEvent;

internal sealed class OrderCancelledDomainEventHandler : IPreCommitDomainEventHandler<OrderCancelledDomainEvent>
{
    private readonly IIntegrationEventPublisher integrationEventPublisher;

    public OrderCancelledDomainEventHandler(IIntegrationEventPublisher integrationEventPublisher)
    {
        this.integrationEventPublisher = integrationEventPublisher;
    }

    public Task HandleAsync(OrderCancelledDomainEvent e, CancellationToken ct = default) =>
        integrationEventPublisher.PublishAsync(new OrderCancelledEvent(e.Order.Id, e.Order.CustomerId, e.Order.CancelledAt), ct);
}

public sealed record OrderCancelledEvent(Guid Id, Guid CustomerId, DateTimeOffset CancelledAt) : IIntegrationEvent;
```

The domain event stays in-process and carries the entity. Any event published out of process through
the broker is an integration event, including one consumed by the same service's own worker. It carries
a flat payload and implements `IIntegrationEvent`. One pre-commit handler per domain event translates
it into the integration event and does nothing else.

Tommy, 2026-10-13: the process boundary defines an integration event, because a service's own worker
needs the same broker contract and atomic outbox guarantee as another service.

`IIntegrationEventPublisher` is the one broker-abstraction role per solution; see
`dotnet:messaging`. Tommy, 2026-10-13: one named publisher role, so no repository invents a
per-subject publisher.

Because the publisher is a transactional outbox, that publish stages a row on the caller's context — so
the state change and the promise to tell the world commit or roll back together. Publishing after the
commit instead is the classic lost-message bug.

**Never let a domain event leave the process.** It is a type in the domain project, holding a live
entity; every broker subscriber receives the integration event.

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
