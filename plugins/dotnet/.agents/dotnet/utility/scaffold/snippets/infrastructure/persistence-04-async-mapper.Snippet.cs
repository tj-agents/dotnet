namespace SnippetFixtures.Persistence04;

internal sealed record Deal;
internal sealed record DealHeader;
internal sealed record SellerHeader;
internal static class Example
{
    private static Task<Dictionary<Guid, Deal>> DealsByIdAsync(IReadOnlyList<SellerHeader> data) => Task.FromResult(new Dictionary<Guid, Deal>());
    private static DealHeader ToDto(SellerHeader item, Dictionary<Guid, Deal> deals) => new();

    public static async Task<IPagination<DealHeader>> Run(IPagination<SellerHeader> page)
    {
// snippet:begin
var deals = await DealsByIdAsync(page.Data).ConfigureAwait(false);
return page.Map(item => ToDto(item, deals));
// snippet:end

    }
}
