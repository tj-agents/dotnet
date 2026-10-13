namespace SnippetFixtures.TestingIntegration01;

using System.Net;
using System.Net.Http.Json;
using Microsoft.EntityFrameworkCore;
using Shouldly;
using Xunit;

public sealed class SeedUser { public Guid Id { get; init; } }
public sealed class SeedState { public SeedUser StandardUser { get; } = new(); }
internal sealed class RunningTotal { public Guid UserId { get; init; } public decimal Value { get; init; } }
internal interface ICalculatorReadDbContext { DbSet<RunningTotal> RunningTotals { get; } }
internal sealed class CalculationResult { public decimal Total { get; init; } }
public sealed class Scoped<T>
{
    private readonly T value;

    public Scoped(T value)
    {
        this.value = value;
    }

    public Task<TResult> RunAsync<TResult>(Func<T, Task<TResult>> work) => work(value);
}
[CollectionDefinition(IntegrationCollection.Name)]
public sealed class IntegrationCollection : ICollectionFixture<ApiFixture>
{
    public const string Name = "Integration";
}
public sealed class ApiFixture
{
    public SeedState SeedState { get; } = new();

    public HttpClient CreateClient(SeedUser user) => new() { BaseAddress = new Uri("https://localhost") };

    public Scoped<T> Scoped<T>() where T : class => new(default!);
}

// snippet:begin
[Collection(IntegrationCollection.Name)]
public sealed class CalculatorApiTests
{
    private readonly ApiFixture fixture;

    public CalculatorApiTests(ApiFixture fixture)
    {
        this.fixture = fixture;
    }

    #region Add

    [Theory]
    [InlineData(2, 3, 5)]
    [InlineData(-1, 1, 0)]
    public async Task Add_TwoOperands_ReturnsTheirSum(int left, int right, int expected)
    {
        var client = fixture.CreateClient(fixture.SeedState.StandardUser);

        var response = await client.PostAsJsonAsync("/api/calculator/add", new { left, right });

        response.StatusCode.ShouldBe(HttpStatusCode.OK);
        var result = await response.Content.ReadFromJsonAsync<CalculationResult>();
        result!.Total.ShouldBe(expected);
    }

    #endregion

    #region Clear

    [Fact]
    public async Task Clear_AfterAnOperation_ResetsTheRunningTotal()
    {
        var client = fixture.CreateClient(fixture.SeedState.StandardUser);
        await client.PostAsJsonAsync("/api/calculator/add", new { left = 4, right = 6 });

        var response = await client.PostAsync("/api/calculator/clear", null);

        response.StatusCode.ShouldBe(HttpStatusCode.OK);
        var total = await fixture.Scoped<ICalculatorReadDbContext>()
            .RunAsync(db => db.RunningTotals.SingleAsync(item => item.UserId == fixture.SeedState.StandardUser.Id));
        total.Value.ShouldBe(0m);
    }

    #endregion
}
// snippet:end
