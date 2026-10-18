namespace SnippetFixtures.ErrorsCarriers06;

internal sealed record WarehouseDetails;
internal abstract record GetWarehouseError
{
    public sealed record WarehouseNotFound : GetWarehouseError;
}

internal interface IWarehouseService2 { Task<Option<WarehouseDetails>> GetDetailsByIdAsync(int id); }

#pragma warning disable CS8321

internal static class Example
{
    public static async Task<Result<WarehouseDetails, GetWarehouseError>> GetAsync(IWarehouseService2 warehouseService, int id)
    {
        // snippet:begin
Result<WarehouseDetails, GetWarehouseError> warehouse = await warehouseService
    .GetDetailsByIdAsync(id)
    .OrFailure<WarehouseDetails, GetWarehouseError>(new GetWarehouseError.WarehouseNotFound())
    .ConfigureAwait(false);

Task<string> ResolveRedirectAsync(Task<Option<string>> redirect) =>
    redirect.ValueOr("/");
// snippet:end

        return warehouse;
    }
}

#pragma warning restore CS8321
