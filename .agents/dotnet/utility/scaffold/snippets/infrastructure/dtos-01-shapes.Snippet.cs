namespace SnippetFixtures.Dtos01;

// snippet:begin
public sealed record VenueSummary(Guid Id, string Name);

public sealed record VenueDto(Guid Id, string Name, string City);

public sealed record Page<T>(IReadOnlyList<T> Items, int TotalCount);
// snippet:end
