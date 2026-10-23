namespace SnippetFixtures.Seeding02;

public sealed record OrderCreatedEvent(Guid Id) : IIntegrationEvent;

public sealed class OrderSeedState
{
    public OrderCreatedEvent OrderCreated { get; } = new(Guid.Parse("61a662e9-123e-4b0c-925d-af7c2bedad8c"));
}

// snippet:begin
public sealed class OrderSeedSimulator
{
    private readonly IIntegrationEventPublisher integrationEventPublisher;
    private readonly OrderSeedState seedState;

    public OrderSeedSimulator(IIntegrationEventPublisher integrationEventPublisher, OrderSeedState seedState)
    {
        this.integrationEventPublisher = integrationEventPublisher;
        this.seedState = seedState;
    }

    public Task SeedAsync(CancellationToken ct = default) =>
        integrationEventPublisher.PublishAsync(seedState.OrderCreated, ct);
}
// snippet:end
