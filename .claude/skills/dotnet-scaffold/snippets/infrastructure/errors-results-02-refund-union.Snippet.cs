namespace SnippetFixtures.ErrorsResults02;

using Dunet;

[Union(EnableImplicitConversions = false)]
public abstract partial record PaymentError : IError
{
    public ErrorDefinition Definition => this switch
    {
        PayerNotFound => ErrorDefinition.NotFound<PayerNotFound>(),
        Declined => ErrorDefinition.PaymentRequired<Declined>("The payment was declined."),
        ProviderFailure => ErrorDefinition.Invalid<ProviderFailure>("The payment provider rejected the request.")
    };

    public partial record PayerNotFound;
    public partial record Declined;
    public partial record ProviderFailure(string ProviderCode);
}

// snippet:begin
[Union(EnableImplicitConversions = false)]
public abstract partial record RefundError : IError
{
    public ErrorDefinition Definition => this switch
    {
        OrderNotFound => ErrorDefinition.NotFound<OrderNotFound>(),
        PaymentFailure(var error) => error.Definition
    };

    public partial record OrderNotFound;
    public partial record PaymentFailure(PaymentError Error);
}
// snippet:end
