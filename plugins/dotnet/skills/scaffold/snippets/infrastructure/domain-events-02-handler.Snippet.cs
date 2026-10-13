namespace SnippetFixtures.DomainEvents02;

public sealed class OrderEntity
{
    public Guid Id { get; init; }
    public Guid CustomerId { get; init; }
    public DateTimeOffset CancelledAt { get; init; }
}

// snippet:begin
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
// snippet:end
