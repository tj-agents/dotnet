namespace Shared;

public interface IIntegrationEvent;

public interface IIntegrationEventPublisher
{
    Task PublishAsync<TEvent>(TEvent integrationEvent, CancellationToken ct = default)
        where TEvent : IIntegrationEvent;
}

public interface IDomainEvent;

public interface IEventRaiser
{
    IReadOnlyList<IDomainEvent> DomainEvents { get; }

    void ClearDomainEvents();
}

public sealed class EventRaiser
{
    private readonly List<IDomainEvent> events = [];

    public IReadOnlyList<IDomainEvent> DomainEvents => events;

    public void Clear() => events.Clear();

    public void Raise(IDomainEvent domainEvent) => events.Add(domainEvent);
}

public interface IDomainEventHandler<TEvent>
    where TEvent : IDomainEvent
{
    Task HandleAsync(TEvent domainEvent, CancellationToken ct = default);
}

public interface IPreCommitDomainEventHandler<TEvent> : IDomainEventHandler<TEvent>
    where TEvent : IDomainEvent;

public interface IIntegrationEventHandler<TEvent>
    where TEvent : IIntegrationEvent
{
    Task HandleAsync(TEvent integrationEvent, CancellationToken ct = default);
}
