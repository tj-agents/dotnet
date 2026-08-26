# Validation

Two different jobs, two different tools. Picking the wrong one produces either a hand-rolled worse
`MaximumLength`, or validation that silently runs twice.

## Input shape is FluentValidation

Required, length, range, enum membership, format, per-property conditions — an
`AbstractValidator<TRequest>`, registered in the owning module's composition root with
`AddValidatorsFromAssemblyContaining<TValidator>(includeInternalTypes: true)`.

Inside an invariant-owning value or entity, reuse the shared domain guard for required text, then perform
trim and length normalization in one plainly named method. Keep that method non-nullable when required
callers have already established the invariant. For the few optional inputs, branch at the call site and
normalize only the present value; do not weaken the common method with nullable input and a nullable
return merely to hide those branches.

**How it is invoked depends on how the input arrives, and this is the part that is easy to get wrong:**

| The input arrives… | How it is validated |
|---|---|
| through an **MVC action** (`[FromBody]`/`[FromForm]`) | `AddFluentValidationAutoValidation()` is registered service-wide, so the filter rejects with a 400 `ValidationProblemDetails` **before the action runs**. Register the validator and stop — do not inject it. |
| **outside the MVC pipeline** — worker, timer job, integration or domain event handler, gRPC server method, in-process module call | Auto-validation is an MVC filter and never runs. Inject `IValidator<TRequest>`, call it explicitly, and map the failure into that operation's own carrier. |

Never inject `IValidator<T>` for a type that *also* reaches the same operation through an MVC action:
auto-validation has already rejected it, so the injected check is unreachable code and its error case is
an outcome the operation cannot produce.

## Domain eligibility is a hand-written validator returning `ValidationResult`

A business precondition that needs other aggregates, other modules, or the clock cannot be expressed
naturally in FluentValidation. That is a hand-written validator returning `ValidationResult` from
`Reunion.Validation` — "is this order still open, in stock, and inside its cancellation window". Its
result composes into the operation's Result chain; it is not an HTTP concern and has no auto-validation
equivalent.

Validator *files* stay named `XValidators` either way; the types inside keep their own shape
(`PlaceOrderRequestValidator`, `OrderValidator`).

## The carrier: `ValidationResult`

```text
ValidationResult = Valid | Invalid(ValidationErrors)
```

`ValidationResult` is the validation-specific facade over `UnitResult<ValidationErrors>`. It fixes the
invalid payload to immutable, non-empty `ValidationErrors`, gives the cases validation vocabulary, and
adds `Combine` for accumulating independent failures while preserving field keys and message order. Its
ordinary composition operations delegate to the inner carrier and are fail-fast. **Never flatten
structured field errors into one string.**

```csharp
ValidationResult validation = new[]
{
    ValidateName(request.Name),
    ValidateEmail(request.Email)
}.Combine();
```

Use `Combine` only for independent validations where reporting every field failure is useful. Business
operations, dependency calls, and state transitions stay fail-fast. Complete all independent validation
and `Combine` it **before** entering ordinary fail-fast composition.

Use `Reunion.Errors.ValidationErrors` everywhere a Result or an operation error carries structured
validation. Do not define, alias, wrap, or convert through a project-owned validation-error carrier.

`ValidationResult` converts implicitly and losslessly to `UnitResult<ValidationErrors>` for assignments
and arguments. C# member lookup does not follow that conversion, which is why Reunion exposes the same
composition surface directly on `ValidationResult`. Raw `ValidationErrors` never convert implicitly into
a success or failure branch.

## Map validation into the operation's own error, once

Validation does not replace the operation's domain error. Map it at the owning operation boundary. Where
the validator has no success payload and the operation must preserve a value it already has, use the
validation-aware `Ensure` overload:

```csharp
return orderModule.GetByIdAsync(orderId)
    .OrFailure<Order, CheckoutError>(new CheckoutError.OrderNotFound(orderId))
    .Ensure(
        order => orderValidator.CanCheckOut(order, quantity),
        errors => new CheckoutError.Invalid(errors));
```

Use validation-aware `Ensure` when a Result already carries the value to preserve, `Map` when validation
genuinely creates a new success value, and `TryGetErrors`/`TryGetFailure` when a standalone validation
guard is the clearest shape. `ToResult` remains available where an explicit carrier conversion fits the
call site.

The owning error union preserves the payload in its definition — see the `result-errors` skill:

```csharp
[Union(EnableImplicitConversions = false)]
public abstract partial record PlaceOrderError : IError
{
    public ErrorDefinition Definition => this switch
    {
        Invalid(var errors) => ErrorDefinition.Validation<Invalid>(errors)
    };

    public partial record Invalid(ValidationErrors Errors);
}
```
