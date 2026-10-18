namespace SnippetFixtures.Proto03;

using System.Collections.Frozen;

internal abstract record OrderError : IError
{
    public ErrorDefinition Definition => ErrorDefinition.NotFound<OrderError>();

    public sealed record CustomerNotFound : OrderError;
    public sealed record AddressRejected : OrderError;
}

internal static class Example
{
// snippet:begin
private static readonly FrozenDictionary<string, OrderError> errors =
    new OrderError[]
    {
        new OrderError.CustomerNotFound(),
        new OrderError.AddressRejected()
    }
    .ToFrozenDictionary(error => error.Definition.Code);
// snippet:end

}
