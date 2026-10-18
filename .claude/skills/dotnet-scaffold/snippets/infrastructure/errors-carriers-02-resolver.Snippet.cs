namespace SnippetFixtures.ErrorsCarriers02;

public sealed record OrderSnapshot;

// snippet:begin
public interface IOrderResolver
{
    Task<Option<OrderSnapshot>> ResolveSnapshotAsync(int orderId, CancellationToken ct = default);
}
// snippet:end
