namespace SnippetFixtures.Validation01;

internal sealed record NameRequest(string Name, string Email);

internal static class Example
{
    private static ValidationResult ValidateName(string name) => ValidationResult.Valid;
    private static ValidationResult ValidateEmail(string email) => ValidationResult.Valid;

    public static void Run(NameRequest request)
    {
// snippet:begin
ValidationResult validation = new[]
{
    ValidateName(request.Name),
    ValidateEmail(request.Email)
}.Combine();
// snippet:end

    }
}
