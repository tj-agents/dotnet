---
name: http-api
description: HTTP contract standard for a .NET service — services return application DTOs and never HTTP-flavoured `Response` types, controllers return the DTO verbatim unless the wire shape genuinely differs, write inputs are `Request` records in `XRequest.cs` files with identity from the route, no ASP.NET Core type in a service signature, action and route-segment naming, the idempotency hash, opt-in rate-limit policies, and translating a domain term into product vocabulary once at the Api layer. Use when adding or changing an endpoint, deciding whether a DTO needs a Response wrapper, shaping a write payload, naming a route or action, or throttling an endpoint.
kind: contract
domain: dotnet
profile: aspnet
applicability: ASP.NET Core HTTP APIs
requires: aspnet-core
provenance: framework, house
---

# HTTP API contracts

Owns the HTTP contract shape — DTO vs Response, write-input `Request` records, route vocabulary and rate limiting.

## Applicability

This contract applies only to ASP.NET Core HTTP APIs. It requires `aspnet-core`. Installing `dotnet@tj-agents` makes this guidance available; it does not select those technologies for a consuming repository.

## Services return DTOs; only the Api layer speaks HTTP

Application services return `Dto` types from the module's application layer, or from its contracts project
for cross-module shapes. **A service never returns an HTTP-flavoured `Response` type** — that keeps it
callable from workers, RPC servers, message handlers, and other non-HTTP consumers.

Controllers return either:

- **the DTO verbatim** — the default, and the right answer for most endpoints; or
- **a `Response` from the Api layer**, where the wire shape genuinely differs from the DTO: versioning,
  role-based shaping, hypermedia, or several endpoints rendering the same DTO differently.

Do not pre-emptively shadow every DTO with a Response.

**One bounded exception:** a **public, anonymous** surface may keep a dedicated `XResponse` even while
it is a field-for-field clone of the DTO. There the Response *is* the frozen wire contract, and its whole
value is that the internal read DTO can grow server-only fields or change projection shape without breaking
public clients. That covers those public reads, not every DTO.

DTO words belong to `dotnet:dtos`. HTTP `Request` and `Response` names describe the boundary contracts defined here; the application keeps its domain-shaped payloads.

## Write inputs are `Request` records

Service write inputs are `Request` types in the application layer — **never the read DTO**, which carries
server-owned fields (`Id`, `UserId`) a caller must not set. Identity comes from the route or method
parameter, not from the body. Request records use `{ get; init; }`.

Where create and update accept the identical writable shape, share **one** `XRequest` rather than duplicating
`CreateXRequest`/`UpdateXRequest`; split them the moment the contracts diverge. One request record lives in
`XRequest.cs`; several belonging to the same resource live in `XRequests.cs`. Never an `XModels.cs`: "model"
names no shape, so the file collects every later contract until a read DTO and a write input share a file and
then a type.

```csharp
public sealed record VenueRequest
{
    public required string Name { get; init; }
    public required int Capacity { get; init; }
}

[HttpPut("api/venue/{venueId:guid}")]
public Task<VenueDto> Update(Guid venueId, VenueRequest request, CancellationToken ct) =>
    venueService.UpdateAsync(venueId, request, ct);
```

Which validator shape a request gets, and whether it is auto-validated or injected, is the `validation`
skill's subject.

A `Request` may carry a framework type for binding, such as an upload's `IFormFile`; a service never
receives one. The controller extracts a plain application shape, a stream plus the metadata the operation
needs, before calling the service. A service signature taking `IFormFile` or any `Microsoft.AspNetCore.*`
type can only be called from inside an HTTP request.

```csharp
public sealed record Attachment(Stream Content, string FileExtension);

public interface IOrderService
{
    Task<OrderDto> PlaceAsync(OrderRequest request, IReadOnlyList<Attachment> attachments, CancellationToken ct);
}
```

## A controller's only query action is `Get`

A controller with exactly one query action names it `Get`: the route and controller already say what it
returns. Once a controller has more than one, name each for what it returns, and none is `Get`.

```text
WarehouseController   Get                       its only query action
OrderController       GetById, GetPending       two query actions, each named for its result
```

## Idempotency is an API-boundary concern

Use the vocabulary of the IETF
[`Idempotency-Key` draft](https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/)
(expired, but the de facto industry term —
[Stripe's idempotent requests](https://docs.stripe.com/api/idempotent_requests) use the same model). The
client sends an `Idempotency-Key` header carrying a UUID; the server stores the `IdempotencyKey` itself
— key, `IdempotencyHash`, outcome — with no `Record`, `Receipt` or `Command` noun. The hash is a SHA-256
the server computes over the fields that define one operation; the client never sends it. A missing key
on an endpoint that requires one is `400`; the same key with a different hash is `422`; a retry while the
original is still processing is `409`; a completed operation with an equal hash replays its stored
outcome. The key stays at the API boundary — domain and application
operations never take it as a concept of their own.

## Translate domain vocabulary into product vocabulary once, at the boundary

Where the product's public term differs from the domain's term, perform the translation **exactly once in the
Api layer**: explicit lowercase route templates and product vocabulary in HTTP models and actions, while
application services, repositories, entities, and database columns keep the domain term throughout. Never
introduce an alias identifier for the same concept below the HTTP boundary — that is two names for one thing
in the layer least able to absorb it.

**Controller ownership follows the resource's domain module.** A shared route prefix alone does not justify a
wrapper controller named after the prefix.

Where a request header or token already selects a scope, do not duplicate that selector in a route or query
string. A zero-or-one relationship is a **singleton sub-resource** (`/api/organization/venue`), not an invented
multi-item collection and not a human-user resource; a canonical entity stays addressable by its own id at
`/api/venue/{venueId}`.

## Name the resource segment once, as a constant

```csharp
[ApiController]
[Route($"api/{RouteSegment}")]
internal sealed class WarehouseController(IWarehouseService warehouseService) : ControllerBase
{
    internal const string RouteSegment = "warehouse";

    [HttpGet($"/api/organization/{RouteSegment}")]
    public Task<WarehouseDto> GetCurrent(CancellationToken ct) => warehouseService.GetCurrentAsync(ct);
}

[ApiController]
[Route($"api/{WarehouseController.RouteSegment}/{{warehouseId:guid}}/reviews")]
internal sealed class WarehouseReviewController : ControllerBase;
```

When a resource's routes span more than one prefix, or a sibling controller nests under it, the owning
controller declares its segment once as `RouteSegment`, and every other route on the resource, including an
absolute per-action override, interpolates that constant.

Why: two literal spellings of one resource drift on the first rename, and the compiler cannot catch a route
that silently stopped matching its sibling.

## Rate limiting

```csharp
services.AddRateLimiter(options =>
{
    options.RejectionStatusCode = StatusCodes.Status429TooManyRequests;
    options.AddPolicy(RateLimitPolicies.SignIn, context =>
        RateLimitPartition.GetFixedWindowLimiter(ClientAddress(context), _ => signInWindow));
    options.AddPolicy(RateLimitPolicies.BulkExport, context =>
        RateLimitPartition.GetFixedWindowLimiter(
            context.User.FindFirstValue(ClaimTypes.NameIdentifier) ?? ClientAddress(context),
            _ => bulkExportWindow));
});
```

An endpoint earns a policy only when it is exposed on the trust axis or the cost axis:

- **Trust:** an anonymous or pre-authentication surface — public browse, sign-in, sign-up, password reset, an
  inbound webhook — is reachable by callers nobody can identify. Partition on the client IP.
- **Cost:** one authenticated call is expensive, such as a multi-source read, bulk export, image processing or
  notification fan-out, or destructive and irreversible, such as a bulk delete or a payment. Partition on the
  authenticated subject, falling back to the client IP when it is absent.

Every other endpoint stays unthrottled. Authentication, admin gating and a naturally low call rate are not
reasons to throttle, so a destructive admin operation is throttled while ordinary admin CRUD is not.

Install no global limiter. Declare one named policy per surface and opt an endpoint in explicitly with
`[EnableRateLimiting(RateLimitPolicies.SignIn)]`. Each policy is a fixed window whose permit limit and window
bind from configuration, and a rejection is `429`. Set a destructive or expensive policy tight enough that
legitimate use never approaches it.

Why: a blanket limiter taxes every request and hides which surfaces are defended; keying a per-user policy
on IP lets one user behind a shared NAT throttle another and lets one user spread across many IPs slip the cap.
Source: [ASP.NET Core rate limiting](https://learn.microsoft.com/aspnet/core/performance/rate-limit).
