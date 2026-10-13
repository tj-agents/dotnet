namespace SnippetFixtures.ErrorsCarriers05;

internal static class Example
{
    public static void Run(string value, string error)
    {
// snippet:begin
Result<string, string> success = new Success<string>(value);
Result<string, string> failure = new Failure<string>(error);
// snippet:end

    }
}
