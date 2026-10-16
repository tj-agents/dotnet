namespace SnippetFixtures.TestingE2E01;

// snippet:begin
using static Microsoft.Playwright.Assertions;

[Binding]
public sealed class ClockSteps
{
    private readonly IPage page;
    private readonly ClockFixture fixture;
    private Guid clockId;

    public ClockSteps(IPage page, ClockFixture fixture)
    {
        this.page = page;
        this.fixture = fixture;
    }

    #region Elapsed

    [Given(@"a clock already started at ""(.*)""")]
    public void GivenAClockAlreadyStartedAt(string start)
    {
        clockId = fixture.SeedState.Clocks[start].Id;
    }

    [When(@"the clock advances to ""(.*)""")]
    public async Task WhenTheClockAdvancesTo(string now)
    {
        await page.GotoAsync($"/clocks/{clockId}").ConfigureAwait(false);
        await page.FillAsync("#now", now).ConfigureAwait(false);
        await page.ClickAsync("#advance").ConfigureAwait(false);
    }

    [Then(@"the elapsed time reads ""(.*)""")]
    public async Task ThenTheElapsedTimeReads(string expected)
    {
        await Expect(page.Locator("#elapsed")).ToHaveTextAsync(expected).ConfigureAwait(false);
    }

    #endregion
}
// snippet:end
