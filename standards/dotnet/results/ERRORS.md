# Typed application errors

Every `TError` is a **closed, operation-owned `XError` union implementing `IError`**. Give every expected
outcome a natural named case, including cases with no payload. Callers match those cases; they never
compare catalog values or parse messages.

## Place the error beside its operation, at its widest in-process caller

- **Domain** when the entity or aggregate operation owns it;
- **Application** when every caller stays inside the module;
- **`*.Contracts`** for cross-module callers;
- a **published client contract** for cross-service client callers.

Do not widen an error union with outcomes the operation cannot produce. Do not create a shared error
catalog, an `ErrorCase` hierarchy, `NotFound<T>` inheritance, `IErrorSet<T>`, marker interfaces, or
wrapper factories that merely rename a case.

## Declare the union with Dunet, implicit conversions off

Disabling Dunet's implicit case conversions keeps the result's branch conversions deliberate:

```csharp
[Union(EnableImplicitConversions = false)]
public abstract partial record PaymentError : IError
{
    public ErrorDefinition Definition => this switch
    {
        PayerNotFound => ErrorDefinition.NotFound<PayerNotFound>(),
        Declined => ErrorDefinition.PaymentRequired<Declined>("The payment was declined."),
        ProviderFailure =>
            ErrorDefinition.Invalid<ProviderFailure>("The payment provider rejected the request.")
    };

    public partial record PayerNotFound;
    public partial record Declined;
    public partial record ProviderFailure(string ProviderCode);
}
```

Derive `Definition` in **one exhaustive switch with no discard arm.** Dunet suppresses `CS8509` only when
every declared case is covered, so an added case must force a deliberate definition and test update — a
default arm throws that guarantee away.

A composite case forwards the nested definition:

```csharp
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
```

Use the generated full `Match` only where delegates are the natural API, and ordinary C# `is` patterns
where logic intentionally inspects selected cases.

**Dunet is for error unions only** — case declarations, exhaustive handling, and genuinely useful full
matches. Do not use it to implement the Result or Option carrier, and do not expose generated `Unwrap` or
case-specific `MatchX` APIs without a concrete need. Result, validation, errors, transports, persistence,
and wire formats stay independent of Dunet.

## Definitions and published codes

Use the direct `Reunion.Errors.ErrorDefinition` generic factories: `Invalid<TCase>()`, `NotFound<TCase>()`,
`Conflict<TCase>()`, `Unauthenticated<TCase>()`, `Forbidden<TCase>()`, `PaymentRequired<TCase>()`,
`Validation<TCase>(errors)`.

Nest each case directly inside its owning union — the generic factories derive the owner from the case's
immediate declaring type. Where a genuinely free-standing error value cannot encode an owner, use the
explicit code-and-message overload; never invent a synthetic owner or a local derivation helper.

Each non-validation factory also has an explicit-message overload. The no-message factory humanizes the
case name, so `PayerNotFound` becomes `Payer not found.` — supply an explicit safe message where the case
name is not the complete caller-facing text. **Never publish exception messages, provider detail, SQL,
stack traces, secrets, or unreviewed identifiers.**

The owning error and case names derive the lowercase dot-separated code: repeated leading owner words and
a trailing `Case` are ignored, while acronyms and digits split naturally, so
`OrderRefundError.OrderNotFound` publishes `order.refund_not_found`.

Use `[ErrorCode("...")]` **only** to preserve an already-published code where a rename or an exceptional
prefix would otherwise change it. It belongs on the case, is not inherited from the union, and is never
decoration added to every case. Never add service-local reflection or code generation to reproduce the
code and message derivation.

Typed error cases never use `[DisplayName]`. Repository entity lookup is a separate concern, where an
entity-oriented helper such as `OrNotFound<TEntity>()` may use the entity type's display name.

## Names and semantic kinds must agree

A `PayerNotFound` case uses `NotFound`. An authenticated caller without permission is `Forbidden`; missing
or invalid identity is `Unauthenticated`. If the semantic kind changes, **rename the case honestly** rather
than leaving a name that lies about the outcome.

## Every union has an exact definition contract test

Cover every case, hard-coding the expected code, message, semantic kind, and validation fields. Keep the
case inventory explicit — never derive test expectations with the production helper or runtime reflection,
which would assert the implementation against itself. Published codes are never renamed or reused for a
different meaning.
