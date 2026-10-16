namespace SnippetFixtures.DomainEvents01;

internal sealed record OrderCancelledDomainEvent(object Order) : IDomainEvent;

public enum OrderStatus { Cancelled }

// snippet:begin
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
// snippet:end
