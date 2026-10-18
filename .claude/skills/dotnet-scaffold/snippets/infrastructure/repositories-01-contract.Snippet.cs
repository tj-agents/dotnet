namespace SnippetFixtures.Repositories01;

public sealed record Order(Guid Id);

// snippet:begin
public interface IOrderRepository
{
    Task<Order?> GetByIdAsync(Guid id, CancellationToken ct = default);
    Task<IReadOnlyList<Order>> GetByCustomerIdAsync(Guid customerId, CancellationToken ct = default);
}
// snippet:end
