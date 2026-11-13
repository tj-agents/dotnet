namespace SnippetFixtures.ErrorsCarriers08;

internal sealed record Refund(Guid RefundId);
internal sealed record RefundResponse(Guid RefundId);

internal static class Example
{
    public static void Run(Option<Refund> refundOption)
    {
// snippet:begin
RefundResponse? refund = refundOption.ToNullable(value => new RefundResponse(value.RefundId));
// snippet:end

    }
}
