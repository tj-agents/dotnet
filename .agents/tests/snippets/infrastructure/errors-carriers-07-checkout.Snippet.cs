namespace SnippetFixtures.ErrorsCarriers07;

internal sealed record Order;
internal sealed record Checkout;
internal abstract record CheckoutError
{
    public sealed record OrderNotFound(int OrderId) : CheckoutError;
    public sealed record Invalid(ValidationErrors Errors) : CheckoutError;
}

internal interface IOrderModule { Task<Option<Order>> GetByIdAsync(int orderId); }
internal interface IOrderValidator { ValidationResult ValidateCheckout(Order order, int quantity); }

internal sealed class Example(IOrderModule orderModule, IOrderValidator orderValidator)
{
    private static Task<Checkout> CreateCheckoutAsync(Order order, int quantity) => Task.FromResult(new Checkout());

    // snippet:begin
public Task<Result<Checkout, CheckoutError>> CheckoutAsync(int orderId, int quantity) =>
    orderModule.GetByIdAsync(orderId)
        .OrFailure<Order, CheckoutError>(new CheckoutError.OrderNotFound(orderId))
        .Ensure(
            order => orderValidator.ValidateCheckout(order, quantity),
            errors => new CheckoutError.Invalid(errors))
        .MapAsync(order => CreateCheckoutAsync(order, quantity));
// snippet:end

}
