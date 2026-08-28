# Result and Option carriers

Reunion is the single carrier family: `Reunion` owns `Result`, `Result<TValue>`,
`Result<TValue, TError>`, `UnitResult<TError>`, `Option<T>`, their named cases, and the composition,
collection and task extensions. Reference the packages a project actually uses **directly** rather than
transitively, keep every Reunion package in one service on the same version, and never redistribute
Reunion through your own shared package — a consumer that needs the carriers references them itself.

Existing code using another carrier or an older construction style is migration debt, not precedent.

## Choose the smallest truthful carrier

Pick the return type from the decisions the caller must make:

| Operation outcome | Return type |
|---|---|
| Success value or expected, actionable failure | `Result<TValue, TError>` |
| Completion or expected, actionable failure | `UnitResult<TError>` |
| Present or ordinarily absent as an intentional application outcome | `Option<T>` |
| Expected failure, otherwise an optional value | `Result<Option<T>, TError>` |
| Provider, storage, framework, wire, or short local value that may be null | `T?` |
| Zero or more values | `IReadOnlyList<T>`; no matches is an empty list |
| No actionable alternate outcome | Plain value, `Task`, or another completion type |
| Capability question only | `bool` |

The short rule: use `T?` for technical nullability that stays in infrastructure or short local plumbing;
use `Option<T>` when `Some(T)` and `None` are the complete, intentional outcomes of an in-process API. If
absence is a named failure, needs an explanation, or must coexist with other failure cases, use
`Result<TValue, TError>`.

**A collection already represents absence with an empty collection.** Never return
`Option<IReadOnlyList<T>>` (or wrap another zero-or-more collection in `Option`) unless `None` is a
genuine, intentional outcome that requires different caller behaviour from `Some(empty)`. If a missing
owner, profile, scope, or filter merely means there are no values to return, use `IReadOnlyList<T>` and
return `[]`. Do not create two representations of “no items” that every caller immediately collapses.

The layer is a strong heuristic, not the decision by itself. Repository and provider lookups normally
return `T?`. Domain, application, module-facade, service, and published client query contracts normally
promote ordinary absence to `Option<T>` so callers cannot reach `T` without observing the case. Commands
and queries with named rejections use a Result. A guaranteed value stays a plain value, and an optional
property on a DTO stays nullable rather than wrapping each field in an Option — converted once at that
boundary, and grouped so values sharing a lifetime become one nullable value object rather than several
independently-nullable fields.

**An expected failure is part of normal control flow** and gives the caller a legitimate branch: not
found, invalid input, conflict, unauthenticated, forbidden, payment required, or another named domain
outcome. Infrastructure faults, violated invariants, programmer errors, and cancellation remain
exceptions.

Use `bool` only for an actual predicate such as `CanAuthenticate`. A command must not return `bool` when
`false` hides several caller actions. Conversely, do not manufacture a Result for uniformity when every
expected outcome is *intentionally* indistinguishable to the caller — a login where bad credentials and
an unknown account are both ordinary absence, precisely to avoid an account-enumeration branch.

A lookup that becomes an HTTP 404 does not automatically need a Result. `GetDetailsByIdAsync` may return
`Option<T>` when found and absent are the whole application contract and the HTTP terminal owns the
`None`-to-404 policy. Use a `NotFound` error case when the missing resource is one of several operation
failures, carries useful detail, or must stay distinguishable outside that terminal.

`Result<TValue>` and non-generic `Result` carry string errors. Keep them to genuinely private, low-level
flows where a string is the complete local contract. Module, application, service, and published client
operations with expected failures use an operation-owned `TError` (see the `result-errors` skill).

**Do not overclaim safety.** `Option<T>` is a distinct runtime value with a non-null payload; NRT
annotations are compiler flow analysis over the same runtime reference type. Option forces conditional
payload extraction but cannot stop a caller ignoring the returned value or a `TryGetValue` boolean.

## Boundary rules

Result and Option are **in-process vocabulary**. They may appear in domain, application, module, and
published C# client signatures. They never appear in:

- HTTP request or response DTOs;
- protobuf messages;
- integration events or messages;
- persistence entities, columns, or repository query contracts;
- configuration or serialized cache contracts.

Each edge maps the carrier to its own wire or storage contract. Repository single-item lookups return
nullable values such as `Task<TEntity?>`, matching the provider's missing-row contract. Convert nullable
to `Option<T>` when ordinary present-or-absent crosses a domain, application, module, service, or client
boundary. Do not push `Option<T>` into EF or repository contracts, and do not wrap a nullable merely to
unwrap it again in the same local flow.

```csharp
public interface IWarehouseReadRepository
{
    Task<WarehouseDetails?> GetDetailsByIdAsync(int warehouseId);
}

public interface IWarehouseService
{
    Task<Option<WarehouseDetails>> GetDetailsByIdAsync(int warehouseId);
}

public async Task<Option<WarehouseDetails>> GetDetailsByIdAsync(int warehouseId) =>
    await repository.GetDetailsByIdAsync(warehouseId);
```

The implicit conversion translates the provider's nullable row into the application's explicit
`Some | None` outcome. A command that *requires* the warehouse instead returns an operation-owned
`Result<WarehouseDetails, UpdateWarehouseError>` with a named `WarehouseNotFound` case.

## Construct with target typing; reach for a named case or factory when the branch is ambiguous

```csharp
Result<User, LookupUserError> found = user;
Result<User, LookupUserError> failed = new LookupUserError.NotFound();

UnitResult<CreateUserError> completed = new Success();
UnitResult<CreateUserError> rejected = new CreateUserError.EmailInUse();

Option<User> present = user;
Option<User> absent = null;
```

So the usual method form is direct:

```csharp
public Option<User> Find(Guid id)
{
    User? user = users.SingleOrDefault(x => x.Id == id);
    return user;
}

public UnitResult<ChangePasswordError> ChangePassword(string password)
{
    if (!IsAllowed(password))
        return new ChangePasswordError.InvalidPassword();

    SetPassword(password);
    return new Success();
}
```

For a target-typed `Option<T>`, prefer `return null;` for `None` and return reference-type payloads
directly — do not write `new None()` or `Option.None<T>()` where the target type already supplies the
conversion. C# cannot apply the `T` conversion to a nullable **value** type (`int?`, `Guid?`, a nullable
value tuple), so use `ToOption()` at those boundaries, and also where an explicit conversion inside a
larger expression reads better or there is no target-typed site. These conversions create an Option;
there is deliberately no implicit conversion back to `T?`.

Use **named cases** where the value and error payload types overlap, where a broad source type would hide
the intended branch, or where the branch itself is the point:

```csharp
Result<string, string> success = new Success<string>(value);
Result<string, string> failure = new Failure<string>(error);
```

A named case preserves its branch. An interface-typed or boxed value follows its declared raw payload
conversion; Reunion does not inspect the runtime type to guess. If C# reports ambiguous operators, make
the branch explicit with a named case.

**Factories** are the universal fallback when there is no target type, inference is unclear, or a factory
is materially easier to read — `Result.Success<object, object>(value)`. Do not mechanically expand clear
target-typed returns into factories, and do not add local wrapper factories around Reunion.

Payload-bearing `Some<T>`, `Success<T>`, and `Failure<TError>` cases reject `null`; `Failure<string>` also
rejects empty or whitespace. Convert nullable values to Option rather than forcing null into a payload
case. Non-generic `Result` and `ValidationResult` use their named cases or factories because they have no
raw payload conversion that identifies a branch.

`default(Option<T>)` is `None`. **Every default Result shape is an invalid, uninitialized union state** —
observing or composing it throws. Never manufacture, return, or treat a default Result as success or
failure.

## Observe and compose

Read payloads through `Match`, `TryGetValue`, or `TryGetError`. There is deliberately no throwing `Value`,
`Error`, or `Unwrap` accessor.

- `Match` at a terminal, or where both branches produce one expression.
- `TryGetValue` / `TryGetError` for a guard clause or early return.
- `IsSuccess` / `IsFailure` / `IsSome` / `IsNone` only where the branch matters but its payload does not.

Compose before the terminal: `Map` transforms a success value; `Bind` chains a same-error operation and
short-circuits failures; `MapError` translates an error at an ownership boundary; `Ensure` turns a failed
success predicate into an owned error; `Tap`/`TapError` perform branch-specific side effects; `OrFailure`
turns an Option into a Result when absence becomes a named failure; `OrElse`/`ValueOr`/`ValueOrElse`
supply Option fallbacks; `Recover`/`RecoverWith` express an intentional recovery policy and never hide a
fault.

**Translate typed failures with `MapError`, matching every case exhaustively.** Never discard a returned
error and construct the failure you believe occurred — that loses the operation's actual outcome and lets
a newly added case map incorrectly.

Prefer the Reunion operation that states the caller's policy over open-coding or locally renaming it:

```csharp
Result<WarehouseDetails, GetWarehouseError> warehouse = await warehouseService
    .GetDetailsByIdAsync(id)
    .OrFailure(new GetWarehouseError.WarehouseNotFound());

Task<string> ResolveRedirectAsync(Task<Option<string>> redirect) =>
    redirect.ValueOr("/");
```

The task extensions apply these operations directly to `Task<Option<T>>` and `Task<Result<…>>`; use
`MatchAsync`, `MapAsync`, `BindAsync`, `OrFailureAsync`, `OrElseAsync`, or `ValueOrElseAsync` where the
supplied callback is itself asynchronous. Do not insert an `await` merely to unpack and reconstruct the
same carrier.

For collections, `Sequence` converts many same-error Results into one, `Traverse`/`TraverseAsync` map then
sequence, and `Combine` collapses unit Results. These are fail-fast and are **not** substitutes for
validation accumulation (see the `validation` skill).

```csharp
public Task<Result<Checkout, CheckoutError>> CheckoutAsync(int orderId, int quantity) =>
    orderModule.GetByIdAsync(orderId)
        .OrFailure<Order, CheckoutError>(new CheckoutError.OrderNotFound(orderId))
        .Ensure(
            order => orderValidator.CanCheckOut(order, quantity),
            errors => new CheckoutError.Invalid(errors))
        .MapAsync(order => CreateCheckoutAsync(order, quantity));
```

Guard-style observation and fluent composition are both valid. Use `TryGetValue` where an early return is
clearest or the missing case has non-Result behaviour such as an invariant exception. Where the
continuation is multi-statement, extract a private operation whose return type honestly distinguishes
`MapAsync` (`Task<TNext>`) from `BindAsync` (`Task<Result<TNext, TError>>`).

The null-coalescing operator works only on nullable operands and cannot be overloaded, so
`option ?? fallback` does not compile and no implicit conversion can make it. Convert explicitly at a
framework edge that genuinely needs a nullable:

```csharp
string? redirect = option.Match<string?>(static value => value, static () => null);
```

Prefer keeping a framework-provided nullable *nullable* where wrapping and immediately unwrapping adds no
application outcome. Do not add local `ToNullable`, `GetValueOrDefault`, or fallback helpers — they
obscure whether the correct contract was nullable, Option, or Result.

Ordinary composition is fail-fast, and combinators do not catch exceptions: cancellation, dependency
failures, and faults pass through the exception path unless an infrastructure adapter explicitly
normalizes a known dependency condition. Normalize to the operation's typed error only when dependency
unavailability is an expected application outcome that callers can act on. When transport retry,
dead-letter, or 503/504 policy owns the failure, preserve it as the explicit dependency exception described
by the `result-terminals` skill. A Result carries error data, never the caught exception itself. Catch only
the dependency exceptions that define the selected policy so cancellation, programmer errors, and
unexpected faults still propagate.

## .NET 11 native unions

Reunion's `net11.0` asset exposes Result and Option as compiler-recognized custom unions. Prefer an
exhaustive switch where both cases drive materially different terminal behaviour:

```csharp
return warehouse switch
{
    Some<WarehouseDetails>(var details) => Render(details),
    None => NotFound()
};
```

Native union matching improves observation ergonomics; it does not change carrier selection. Repositories,
EF, serialization, and nullable framework APIs still use `T?`, and `??` still does not apply to Option.

## Never introduce

- another Result, Option, validation, or application-error carrier — including
  `CSharpFunctionalExtensions`, `FluentResults`, `OneOf`, `ErrorOr`, or `LanguageExt`;
- a Result or Option in a wire, event, persistence, or serialized DTO;
- a nullable repository contract changed to Option;
- a zero-or-more collection wrapped in Option when None has no caller-visible meaning beyond empty;
- a bool or enum that collapses caller-actionable outcomes;
- a throwing payload accessor, or a default Result treated as a branch;
- broad exception-to-domain-error conversion;
- `new None()` / `Option.None<T>()` where a target-typed `null` is the clear Option result;
- factory-heavy construction where a raw target-typed payload is unambiguous.
