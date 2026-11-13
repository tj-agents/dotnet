namespace SnippetFixtures.HttpApi03;

using Microsoft.AspNetCore.Mvc;

internal sealed record WarehouseDto(Guid Id, string Name);

internal interface IWarehouseService
{
    Task<WarehouseDto> GetCurrentAsync(CancellationToken ct);
}

// snippet:begin
[ApiController]
[Route($"api/{RouteSegment}")]
internal sealed class WarehouseController(IWarehouseService warehouseService) : ControllerBase
{
    internal const string RouteSegment = "warehouse";

    [HttpGet($"/api/organization/{RouteSegment}")]
    public Task<WarehouseDto> GetCurrent(CancellationToken ct) => warehouseService.GetCurrentAsync(ct);
}

[ApiController]
[Route($"api/{WarehouseController.RouteSegment}/{{warehouseId:guid}}/reviews")]
internal sealed class WarehouseReviewController : ControllerBase;
// snippet:end
