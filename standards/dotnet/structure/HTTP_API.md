# HTTP API contracts

## Services return DTOs; only the Api layer speaks HTTP

Application services return `Dto` types from the module's application layer, or from its contracts project
for cross-module shapes. **A service never returns an HTTP-flavoured `Response` type** — that keeps it
callable from workers, RPC servers, message handlers, and other non-HTTP consumers.

Controllers return either:

- **the DTO verbatim** — the default, and the right answer for most endpoints; or
- **a `Response` from the Api layer**, where the wire shape genuinely differs from the DTO: versioning,
  role-based shaping, hypermedia, or several endpoints rendering the same DTO differently.

Do not pre-emptively shadow every DTO with a Response.

**One bounded exception:** a **public, anonymous** surface may keep a dedicated `XDetailsResponse` even while
it is a field-for-field clone of the DTO. There the Response *is* the frozen wire contract, and its whole
value is that the internal read DTO can grow server-only fields or change projection shape without breaking
public clients. That covers the public details reads, not every DTO.

Drop the `Dto` suffix where the name already says what the shape is; keep it only to disambiguate from a
same-named entity. Full suffix rules are in the `csharp-naming` skill.

## Write inputs are `Request` records

Service write inputs are `Request` types in the application layer — **never the read DTO**, which carries
server-owned fields (`Id`, `UserId`) a caller must not set. Identity comes from the route or method
parameter, not from the body. Request records use `{ get; init; }`.

Where create and update accept the identical writable shape, share **one** `XRequest` rather than duplicating
`CreateXRequest`/`UpdateXRequest`; split them the moment the contracts diverge.

Which validator shape a request gets, and whether it is auto-validated or injected, is the `validation`
skill's subject.

**A `Request` may carry a framework type for binding/validation; a service never receives that type.** An
upload's `IFormFile`, or any other ASP.NET Core type on a `Request`, is extracted into a plain
application-layer shape (a stream plus the metadata the operation needs) before the service is called. A
service signature that takes `IFormFile` (or any `Microsoft.AspNetCore.*` type) can only be called from
inside an HTTP request — the one thing "service" is supposed not to mean.

```csharp
// WRONG — the service now requires an HTTP multipart pipeline to be reachable at all
Task<Result<Order, PlaceOrderError>> PlaceAsync(PlaceOrderRequest request); // request.Attachment is IFormFile

// CORRECT — the controller extracts what the operation actually needs
Task<Result<Order, PlaceOrderError>> PlaceAsync(IReadOnlyList<Attachment> attachments);
public sealed record Attachment(Stream Content, string FileExtension);
```

## Name a controller's single query action `Get`; disambiguate only past one

A controller with exactly one query action names it `Get` — the route and controller already say what it
returns. The moment a controller has more than one, name each for what it returns; `Get` stops being legal
on any of them, since none is *the* query anymore.

```csharp
// CORRECT — one query action, no name needed beyond "Get"
internal sealed class WarehouseController : ControllerBase
{
    [HttpGet]
    public Task<ActionResult<WarehouseDetails>> Get(CancellationToken ct) => ...;
}

// CORRECT — more than one query action, each named for its result
internal sealed class OrderController : ControllerBase
{
    [HttpGet("{id}")]
    public Task<ActionResult<OrderDetails>> GetById(int id, CancellationToken ct) => ...;

    [HttpGet("pending")]
    public Task<ActionResult<IPagination<OrderSummary>>> GetPending([FromQuery] PageParams page) => ...;
}
```

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
