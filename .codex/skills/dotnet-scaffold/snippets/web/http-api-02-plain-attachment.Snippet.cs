namespace SnippetFixtures.HttpApi02;

public sealed record OrderDto(Guid Id);

public sealed record OrderRequest
{
    public required string Reference { get; init; }
}

// snippet:begin
public sealed record Attachment(Stream Content, string FileExtension);

public interface IOrderService
{
    Task<OrderDto> PlaceAsync(OrderRequest request, IReadOnlyList<Attachment> attachments, CancellationToken ct);
}
// snippet:end
