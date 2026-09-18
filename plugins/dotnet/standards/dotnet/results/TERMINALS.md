# Result terminals

A Result is in-process vocabulary; a terminal is the one place it becomes a response. Map **only** at the
controller, endpoint, worker, or RPC-server boundary — never halfway down the call stack.

## HTTP

HTTP projects use `Reunion.AspNetCore` directly, and **import exactly one adapter namespace per source
file**: `Reunion.AspNetCore.HttpResults` for `TypedResults` and `Results<T1, T2>`, or
`Reunion.AspNetCore.Mvc` for `ActionResult<T>` and `ActionResult`. Never import both — the identical
terminal method names are intentionally ambiguous between the two programming models.

| Terminal | For |
|---|---|
| `ToOkOrProblem` | value Results |
| `ToNoContentOrProblem` | unit Results |
| `ToCreatedOrProblem` | a Result whose normal success is Created |
| `ToCreatedAtActionOrProblem` | Created where MVC route generation owns the location |
| `ToActionResult` / `ToResults` | custom success mapping (MVC / typed HTTP results) |
| `ToOkOr` | an Option whose absence maps to a caller-supplied result |
| `ToOkOrNotFound` / `ToOkOrNoContent` | an Option where HTTP owns that absence policy |

**Use a terminal's projected overload rather than a `Map` immediately before it.** Do not `Map` into a
wire type and then call `ToOkOrProblem` — the terminal performs the projection itself. Pass controller
result methods directly where no extra state is needed:

```csharp
return user.ToOkOr(Unauthorized);
return artist.ToOkOr(value => value.ToDetailsResponse(), NotFound);
return artistResult.ToOkOrProblem(value => value.ToDetailsResponse());
```

For `TError : IError`, **omit the problem mapper**. Reunion maps `Invalid`/`NotFound`/`Conflict`/
`Unauthenticated`/`Forbidden`/`PaymentRequired` to 400/404/409/401/403/402, includes the stable code, and
preserves a validation error as field-indexed `ValidationProblemDetails`. String-error Results always need
an explicit safe problem mapper with an explicit status.

Both programming models participate in `IProblemDetailsService`, so registered writers, content
negotiation, request instance, trace identifiers, and configured customization stay consistent.
**Never throw an HTTP exception to transport an expected Result failure.**

## gRPC

The wire never carries a union type or a Result. Client-side reverse mapping, the reconstructible-case
dictionary, contract-mismatch handling, and cancellation precedence are the `proto` skill's subject —
read it when the terminal is an RPC boundary.

## Exceptions, cancellation, and workers

An infrastructure adapter may normalize a **known** provider unavailability or deadline fault into
`DependencyUnavailableException` or `DependencyTimeoutException`, preserving the provider exception as the
inner exception. HTTP maps only those explicit types to safe 503/504 responses. Broad
`HttpRequestException`, `RpcException`, `TimeoutException`, database exceptions, and unknown faults remain
safe 500s.

**Cancellation is never normalized into an error Result and never handled as an HTTP response.** Propagate
the caller's token and preserve cancellation semantics.

At worker and RPC-server terminals, match expected typed failures according to the operation's policy, and
leave dependency exceptions on the exception path so retry and dead-letter behaviour still works. Do not
catch broad exceptions and translate them into a generic domain error.

## What a Result-based change owes its tests

In proportion to the operation:

- every success, failure, `Some`, and `None` branch;
- the exact definition contract for every error case;
- validation accumulation and field preservation;
- privacy-equivalent branches, such as unknown account versus bad credential;
- exception and cancellation propagation;
- HTTP status, code, ProblemDetails customization, and validation fields at the terminal;
- RPC reverse-map completeness, duplicate codes, mismatches, and cancellation precedence;
- architecture rules that keep a legacy or alternate carrier from returning;
- exact package versions, with no mixed carrier-package graph.

Build and test a service against its **standalone package closure**, not only the source graph it happens
to sit in. A published contract change follows a publish-then-consume cut-over.
