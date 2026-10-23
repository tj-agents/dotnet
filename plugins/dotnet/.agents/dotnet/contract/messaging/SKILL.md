---
name: messaging
description: Integration-event messaging roles — the one generic `IIntegrationEventPublisher` per solution, staging events in the caller's unit of work, and the `<Subscription>Processor` `BackgroundService` that pumps one broker subscription, dispatches each message to its `<Event>Handler` in a fresh scope and settles it. Use when publishing an integration event, consuming a broker subscription, or naming either role.
kind: contract
domain: dotnet
profile: distributed-services
applicability: services publishing or consuming integration events through a message broker
requires: message-broker
provenance: architecture, house
---

# Messaging

Owns the integration-event publisher role and the processor that pumps a broker subscription.

## Applicability

This contract applies to services that publish or consume integration events through a message broker.
`dotnet:domain-events` owns the domain-event/integration-event boundary and the pre-commit translation,
including broker events consumed by the same service's own worker. Reacting to a message is the Handler
role in `dotnet:naming-collaborators`.

## Publish through the one generic publisher

`IIntegrationEventPublisher.PublishAsync<TEvent>` stages the event in the outbox, committing with the
caller's unit of work.

```csharp
public interface IIntegrationEventPublisher
{
    Task PublishAsync<TEvent>(TEvent integrationEvent, CancellationToken ct = default)
        where TEvent : IIntegrationEvent;
}
```

`IIntegrationEventPublisher` is the one broker-abstraction role per solution, generic over the event type.

## The Processor pumps a subscription, the Handler reacts to it

The role that pumps a broker subscription is `<Subscription>Processor` — `OrderEventsProcessor`, a
`BackgroundService` in Infrastructure that owns one subscription, dispatches each received message to
its `<Event>Handler`, then settles the message. Each received message is settled — complete, abandon or
dead-letter — once its handler has run. Rejected names: `HostedService` (names the host mechanism, not the
role), `Consumer` (already the Handler's role in some broker SDKs), `Worker` (no contract), `Listener` and
`Subscriber` (both read as the handler).

```csharp
internal sealed class OrderEventsProcessor : BackgroundService
{
    private readonly ServiceBusProcessor processor;
    private readonly IServiceScopeFactory scopeFactory;
    private readonly ILogger<OrderEventsProcessor> logger;

    public OrderEventsProcessor(
        ServiceBusProcessor processor,
        IServiceScopeFactory scopeFactory,
        ILogger<OrderEventsProcessor> logger)
    {
        this.processor = processor;
        this.scopeFactory = scopeFactory;
        this.logger = logger;
        processor.ProcessMessageAsync += HandleMessageAsync;
        processor.ProcessErrorAsync += HandleErrorAsync;
    }

    protected override Task ExecuteAsync(CancellationToken stoppingToken) =>
        processor.StartProcessingAsync(stoppingToken);

    public override async Task StopAsync(CancellationToken cancellationToken)
    {
        await processor.StopProcessingAsync(cancellationToken).ConfigureAwait(false);
        await base.StopAsync(cancellationToken).ConfigureAwait(false);
    }

    private async Task HandleMessageAsync(ProcessMessageEventArgs args)
    {
        var integrationEvent = args.Message.Body.ToObjectFromJson<OrderPlacedEvent>();

        var scope = scopeFactory.CreateAsyncScope();
        await using (scope.ConfigureAwait(false))
        {
            var handler = scope.ServiceProvider.GetRequiredService<IIntegrationEventHandler<OrderPlacedEvent>>();
            await handler.HandleAsync(integrationEvent, args.CancellationToken).ConfigureAwait(false);
        }

        await args.CompleteMessageAsync(args.Message, args.CancellationToken).ConfigureAwait(false);
    }

    private Task HandleErrorAsync(ProcessErrorEventArgs args)
    {
        logger.SubscriptionProcessingFailed(args.EntityPath, args.Exception);
        return Task.CompletedTask;
    }
}
```

`<Subscription>Processor` is the one role for the hosted loop that pumps a broker
subscription. It takes explicit `private readonly` fields assigned with `this.` in the constructor, never a primary-constructor
capture, and uses the broker SDK's own type (`ServiceBusProcessor` above) as the receive source rather
than inventing a receiver role. It dispatches each message to its `<Event>Handler` in a fresh DI scope, because the processor is a
singleton and handlers are scoped, then settles the message itself: the Handler owns only the business
reaction, never the settlement. A handler that throws leaves the message unsettled, so the broker
redelivers it and dead-letters it after its maximum delivery count. Register the `ServiceBusProcessor`
with `AutoCompleteMessages = false`.
