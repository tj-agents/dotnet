namespace SnippetFixtures.Validation02;

internal sealed record Order;
internal abstract record CheckoutError
{
    public sealed record OrderNotFound(int OrderId) : CheckoutError;
    public sealed record Invalid(ValidationErrors Errors) : CheckoutError;
}

internal interface IOrderModule { Task<Option<Order>> GetByIdAsync(int orderId); }
internal interface IOrderValidator { ValidationResult ValidateCheckout(Order order, int quantity); }

internal static class Example
{
    public static Task<Result<Order, CheckoutError>> Run(IOrderModule orderModule, IOrderValidator orderValidator, int orderId, int quantity)
    {
        // snippet:begin
return orderModule.GetByIdAsync(orderId)
    .OrFailure<Order, CheckoutError>(new CheckoutError.OrderNotFound(orderId))
    .Ensure(
        order => orderValidator.ValidateCheckout(order, quantity),
        errors => new CheckoutError.Invalid(errors));
// snippet:end

    }
}
