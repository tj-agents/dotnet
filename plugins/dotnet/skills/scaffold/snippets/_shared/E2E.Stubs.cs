global using Microsoft.Playwright;
global using Reqnroll;

namespace SnippetFixtures.TestingE2E01;

public sealed class ClockFixture
{
    public ClockSeedState SeedState { get; } = new();
}

public sealed class ClockSeedState
{
    public IReadOnlyDictionary<string, ClockSeed> Clocks { get; } = new Dictionary<string, ClockSeed>(StringComparer.Ordinal);
}

public sealed record ClockSeed(Guid Id);
