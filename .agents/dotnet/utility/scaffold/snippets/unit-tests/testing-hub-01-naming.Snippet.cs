namespace SnippetFixtures.TestingHub01;

using Xunit;

internal sealed class Calculator
{
    public int Add(int left, int right) => left + right;
}

public sealed class CalculatorNamingExample
{
    private readonly Calculator calculator = new();

    [Theory]
    [InlineData(2, 3, 5)]
    // snippet:begin
public void Add_TwoOperands_ReturnsTheirSum(int left, int right, int expected)
// snippet:end

    {
        var result = calculator.Add(left, right);

        Assert.Equal(expected, result);
    }
}
