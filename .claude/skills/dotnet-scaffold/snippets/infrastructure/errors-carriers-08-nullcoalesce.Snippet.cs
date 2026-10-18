namespace SnippetFixtures.ErrorsCarriers08;

internal static class Example
{
    public static void Run(Option<string> option)
    {
// snippet:begin
string? redirect = option.Match<string?>(static value => value, static () => null);
// snippet:end

    }
}
