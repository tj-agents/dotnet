namespace SnippetFixtures.Authorization04;

public readonly record struct Permission(string Value);

public sealed record ResourceAddress(string Type, Guid Id);

// snippet:begin
public sealed record AccessRequest(Permission Action, ResourceAddress Resource);

public interface IAccessDecision
{
    Task<bool> IsAllowedAsync(AccessRequest request, CancellationToken ct = default);
}
// snippet:end
