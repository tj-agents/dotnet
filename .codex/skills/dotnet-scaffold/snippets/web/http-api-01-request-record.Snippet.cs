namespace SnippetFixtures.HttpApi01;

using Microsoft.AspNetCore.Mvc;

internal sealed record VenueDto(Guid Id, string Name, int Capacity);

internal interface IVenueService
{
    Task<VenueDto> UpdateAsync(Guid venueId, VenueController.VenueRequest request, CancellationToken ct);
}

[ApiController]
internal sealed class VenueController(IVenueService venueService) : ControllerBase
{
// snippet:begin
public sealed record VenueRequest
{
    public required string Name { get; init; }
    public required int Capacity { get; init; }
}

[HttpPut("api/venue/{venueId:guid}")]
public async Task<VenueDto> Update(Guid venueId, VenueRequest request, CancellationToken ct) =>
    await venueService.UpdateAsync(venueId, request, ct);
// snippet:end

}
