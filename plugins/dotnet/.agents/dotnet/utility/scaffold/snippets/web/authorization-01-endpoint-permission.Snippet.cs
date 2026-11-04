namespace SnippetFixtures.Authorization01;

using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

internal sealed class HasPermissionAttribute(string permission) : AuthorizeAttribute(permission);

internal static class Permission
{
    public const string SettlementTriggerName = "settlement.trigger";
}

internal sealed record SettlementDto;

internal interface ISettlementService
{
    Task<SettlementDto> TriggerAsync(Guid concertId, CancellationToken ct);
}

[ApiController]
internal sealed class SettlementController : ControllerBase
{
    private readonly ISettlementService settlements;

    public SettlementController(ISettlementService settlements) => this.settlements = settlements;

// snippet:begin
[HasPermission(Permission.SettlementTriggerName)]
public Task<SettlementDto> Trigger(Guid concertId, CancellationToken ct) =>
    settlements.TriggerAsync(concertId, ct);
// snippet:end

}
