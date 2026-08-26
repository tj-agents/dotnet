# C# naming

## Pick a suffix from the type's shape, not from "it's injectable"

`Service` is the suffix that rots first: it gets used for anything injectable, and once a pure
value-producer is also a `Service`, the genuinely useful smell — *a service calling another service* —
stops being visible, because every collaborator looks the same at the injection site. Almost everything
is DI-registered; that fact carries no naming information.

| Suffix | The shape it claims | Framework precedent |
|---|---|---|
| `Service` | Orchestrates domain logic **over a repository**. Stateful collaborator, owns a unit of work. | — |
| `Repository` | Domain-entity persistence via a `DbContext`. | — |
| `Store` | Bytes/blobs in and out of a backing store, no domain logic. | `IUserStore` |
| `Client` | A remote or third-party API. | `HttpClient`, `BlobServiceClient` |
| `Factory` | Creates **instances/components**, usually of a type family. | `IHttpClientFactory`, `ILoggerFactory` |
| `Generator` | Produces a **value/artifact** from inputs. | `LinkGenerator`, `RandomNumberGenerator` |
| `Builder` | **Mutable, stepwise** accumulation terminated by `Build()` or a final property. | `StringBuilder`, `UriBuilder`, `WebApplicationBuilder` |
| `Provider` | Supplies a value or a pluggable strategy, often one of several. | `IServiceProvider`, `IFileProvider`, `TimeProvider` |
| `Accessor` | Exposes an ambient/current value. | `IHttpContextAccessor` |
| `Handler` | Reacts to a message or event. | — |
| `Helper` / `Utility` | **`static class` of pure functions.** No DI, no state, no config. | `WebUtility`, `HttpUtility` |

The precedent column is the calibration: `StringBuilder` accumulates then finalizes, `RandomNumberGenerator`
returns a value from inputs, `IHttpClientFactory` hands back a component. A dash means the framework offers
no anchor and the definition above is the whole rule.

Two rules follow from the table:

- **`Helper`/`Utility` is reserved for `static`.** It is not the escape hatch for "injected but not
  really a service" — an injected, config-bound collaborator gets a shape noun (`Generator`, `Factory`,
  `Store`). The framework is itself inconsistent here (`IUrlHelper` is injected), which is exactly why
  the stricter meaning is pinned rather than inherited.
- **`Builder` vs `Generator` vs `Factory` is decided by mechanics, not vibes** — mutable-then-finalize
  is a `Builder`, a one-shot value from inputs is a `Generator`, a one-shot *component* is a `Factory`.

A separate factory or generator must represent a real construction collaborator, a family of outputs, or
construction owned by an outer layer. When creation is the owned type's own domain behavior and the
separate type only constructs that one type, put a named static creation method on the owned type. Keep
infrastructure, test, and seed construction outside the domain type; the seeding-specific factory shape is
owned by the `seeding` skill. Keep each top-level request, result, status, and execution shape in the
correspondingly named file; do not collect unrelated roles in a generic `Models` file.

**A type whose whole job is one operation is named for the agent-noun of that method** —
`Mapper.Map`, `Resolver.Resolve`, `Calculator.Calculate`, `Renderer.Render`, `Serializer.Serialize`.
The table above is the same rule widened to collaborator shapes.

**A qualifier only exists to contrast with a sibling.** `PublicXRepository` with no `AdminXRepository`
to disambiguate from is noise — name it `XRepository` and rename the day the second stance is born.

## Name a repository method for the query, a service method for the intent

A repository finder says literally what it fetches and by what key — `GetByCustomerIdAsync`,
`GetUnreadCountByCustomerIdAsync` — so the data access is obvious at the call site. The use-case name
(`GetInboxAsync`, `GetInboxSummaryAsync`) belongs on the *service* that calls it. Never push an intent
name down onto the repository.

Reserve `CurrentUser`, `ForUser`, `Me`, and `Self` for data belonging to the authenticated human. Do not
append a scope word to every method merely to restate the default scope; name the ordinary use case for
its domain intent and name the *alternative* capability explicitly (`GetDetailsByIdAsync`).

## `Response` is HTTP-only; `Dto` is a deliberate disambiguator

- The `Response` suffix belongs to the **HTTP wire layer** only. It does not belong on the C#
  service/client payloads that adapters pass around: a typed result wrapper is already the
  "did it succeed" envelope, so `Result<XResponse, XError>` double-encodes "this is a reply".
- **Payloads do not mechanically gain or lose `Dto`.** Keep the suffix where it usefully distinguishes a
  data shape from a same-named entity or domain concept (`OrderDto`); omit it where the payload name is
  already unambiguous (`Shipment`, `Refund`, `Invoice`). Accept an SDK name collision and resolve it with
  a `using` alias in the few files that need both types.

```csharp
// CORRECT — unambiguous payloads need no suffix
Task<Result<Shipment, DispatchError>> DispatchAsync(...);

// CORRECT — Dto distinguishes the data shape from the Order entity
Task<Result<OrderDto, OrderError>> GetByIdAsync(int id);

// WRONG — wire suffix on a non-HTTP payload, redundant with the typed Result
Task<Result<ShipmentResponse, DispatchError>> DispatchAsync(...);
```

Proto message names are a separate case and stay `*Response` — see the `proto` skill.

## `Projection` names an intermediate query shape, nothing else

Name a query result for the role it plays, not for the layer that returned it:

- A repository returning a persistence entity or a persisted read model returns that type directly.
- A repository returning the final meaningful application shape uses that shape's normal name. Do not
  add `Projection` merely because a repository materialized it.
- Use `Projection` only for an ephemeral `Select` shape the service must map or enrich before returning
  its own result, and keep that type internal to the repository/application boundary.
- `Dto` and `Projection` are not synonyms. `Projection` describes an intermediate query shape; `Dto`
  identifies a data contract where the suffix genuinely disambiguates.
- If a repository and a service return the same final type, do not introduce a throwaway mapping type.

## Type-to-type mapping lives in an `XMappers` extension class

Mapping goes in a static `XMappers` class as extension methods named for the target, never as private
`MapX` helpers on the consumer.

```csharp
internal static class ShipmentMappers
{
    extension(ShipmentEntity entity)
    {
        public Shipment ToShipment() => ...;
    }

    extension(ShipmentStatusCode code)
    {
        public ShipmentStatus ToShipmentStatus() => ...;
    }
}
```

## Receiver-owned behaviour is an extension; a decision over peers is a named evaluator

A pure operation belongs on an extension when one receiver clearly owns the transformation or question.
Use the shortest unambiguous domain name: `value.ToDto()`, `reading.ToNormalized()`,
`state.IsTerminal()`. Keep a receiver's related extensions in one `XExtensions` class, or in the mapping
family's `XMappers` class; do not scatter them across unrelated helpers.

A decision over two or more peer inputs belongs to neither receiver. Keep the policy visible at the call
site behind an operation-specific static type such as `TransitionEvaluator.Evaluate(current, observed)`.
Do not call an evaluator a `Specification` unless you mean query-specification semantics.

Use an exhaustive switch in an `XMappers` extension for a small closed enum conversion. A
`FrozenDictionary` or `FrozenSet` is for a deterministic table whose entries are materially easier to
inspect and maintain as data — provider-status normalization, fixed error definitions, or legal transition
edges — not a lookup-shaped replacement for a two-case switch. Use guarded code when the outcome depends
on contextual validation or calculation. Where the entries are *behaviour* selected by a closed key, use
the validated registry in the `keyed-strategies` skill instead — never a parallel frozen map per consumer.
