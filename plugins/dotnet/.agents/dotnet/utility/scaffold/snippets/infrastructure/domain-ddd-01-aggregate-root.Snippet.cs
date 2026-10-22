namespace SnippetFixtures.DomainDdd01;

public enum OrderStatus { Placed, Shipped, Cancelled }

// snippet:begin
public sealed class Order
{
    public Guid Id { get; }
    public Guid CustomerId { get; }
    public OrderStatus Status { get; private set; }

    public void Cancel()
    {
        if (Status == OrderStatus.Shipped)
            throw new InvalidOperationException("A shipped order cannot be cancelled.");
        Status = OrderStatus.Cancelled;
    }
}
// snippet:end
