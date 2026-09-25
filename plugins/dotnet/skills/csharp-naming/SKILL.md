---
name: csharp-naming
description: Generic C# naming standard — choose the domain concept and existing owner before a suffix; distinguish repository queries, service orchestration, resolvers and lookup data structures; name data shapes by their meaning rather than generic Fact/Facts, Info, Data or Model suffixes; use Snapshot only for captured state. Covers collaborator suffixes, interface/implementation pairs, keyed finder names, HTTP-only Response, deliberate Dto, intermediate Projection, XMappers and policy evaluators. Use when designing or reviewing types, members, contracts or plan snippets, especially when a proposed name obscures responsibility or duplicates an existing owner.
kind: contract
domain: dotnet
profile: core
applicability: all C# and .NET code
requires: none
provenance: language, house
---

# C# naming

## Applicability

This contract applies to every C#/.NET repository and has no application-stack prerequisite.

## Choose the domain concept and its owner before the suffix

Read the type's contract, implementation and callers before naming it. Reuse the domain noun and the
existing owner of that responsibility. Within one bounded context, the same concept keeps the same word
across types, members, parameters and contracts; a different word must describe a real semantic difference.

A suffix states a contract the implementation must satisfy. DI registration, an async method, a record
declaration or a read-only operation does not decide that contract. Add an operation to its cohesive owner
before inventing another collaborator; renaming a misplaced query does not fix its ownership.

Follow the [framework type-naming guidance](https://learn.microsoft.com/en-us/dotnet/standard/design-guidelines/names-of-classes-structs-and-interfaces):
types use noun phrases and methods use verb phrases. An ordinary interface/implementation pair shares its
name apart from the interface's `I`; qualify an implementation only for a real alternate strategy or role.
A capability interface (`IDisposable`, `IPausable`) keeps its `-able` word to itself: each implementation is
named for what it is or acts on (`OutboxDispatcher`, `HostPauser`), never `XPausable`, `PausableX` or a
pattern name such as `Composite`. Use the repository's established vocabulary consistently in proposed code as well as executable code.

## Pick a suffix from the type's shape, not from "it's injectable"

`Service` is the suffix that rots first: it gets used for anything injectable, and once a pure
value-producer is also a `Service`, the genuinely useful smell — *a service calling another service* —
stops being visible, because every collaborator looks the same at the injection site. Almost everything
is DI-registered; that fact carries no naming information.

| Suffix | The shape it claims | Framework precedent |
|---|---|---|
| `Service` | Orchestrates a domain use case over repositories; owns the unit of work when the use case writes. | — |
| `Repository` | Domain-entity persistence and queries, including read-only queries and projections, via a `DbContext`. | — |
| `Store` | Opaque bytes/blobs in and out of a backing store, no domain operations. | — |
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

**A focused operation collaborator uses the agent-noun of its operation** —
`Mapper.Map`, `Resolver.Resolve`, `Calculator.Calculate`, `Renderer.Render`, `Serializer.Serialize`,
`Exporter.Export`. Operation count does not override responsibility: a repository with one finder is
still a repository, and a service with one business operation is still a service. A resolver applies
selection or resolution rules; fetching an entity by its key remains a repository query.

**A role qualifier only exists to contrast with a sibling.** `PrimaryOrderResolver` with no
`FallbackOrderResolver` to disambiguate from is noise — name it `OrderResolver` and rename the day
the second role is born. A capability or shape qualifier such as `Read` or `Snapshot` instead states
a real contract or guarantee and does not require a sibling.

## Keep database queries on repositories

Name a database-backed entity query with repository vocabulary even when it returns a projection,
exposes only reads, or serves authorization. A service adds use-case rules or orchestration; it does
not earn its name by forwarding one finder.

`Lookup` describes an indexed data structure or view, such as
[`ILookup<TKey,TElement>`](https://learn.microsoft.com/en-us/dotnet/api/system.linq.ilookup-2?view=net-10.0).
`OrderRepository.GetByIdAsync(id)` communicates persistence; `OrderLookup.GetAsync(id)` obscures it.
`Lookup`, `Facts`, `Provider` and `Store` are not substitute names for repository-owned queries.
Repository placement is defined in `dotnet:persistence`; consumer boundaries plus stance
and projection ownership are defined in `dotnet:multitenancy`. Follow those owners to
decide whether a separate repository capability is warranted.

Framework-owned contracts retain their framework names. ASP.NET Core
[`IUserStore<TUser>`](https://learn.microsoft.com/en-us/dotnet/api/microsoft.aspnetcore.identity.iuserstore-1?view=aspnetcore-10.0)
manages user accounts; its established name is not the precedent for naming our entity repositories.

## Name a repository method for the query, a service method for the intent

A repository finder says literally what it fetches and by what key — `GetByCustomerIdAsync`,
`GetUnreadCountByCustomerIdAsync` — so the data access is obvious at the call site. The use-case name
(`GetInboxAsync`, `GetInboxSummaryAsync`) belongs on the *service* that calls it. Never push an intent
name down onto the repository.

Reserve `CurrentUser`, `ForUser`, `Me`, and `Self` for data belonging to the authenticated human. Do not
append a scope word to every method merely to restate the default scope; name the ordinary use case for
its domain intent and name the *alternative* capability explicitly (`GetDetailsByIdAsync`).

## Name a data shape for what it represents

Use the domain noun first. Add a qualifier only when it identifies a real shape or guarantee:

| Shape | Name communicates |
|---|---|
| `OrderSummary` / `OrderDetails` | The actual summary or detail contract |
| `OrderStatus` | Lifecycle state |
| `OrderSnapshot` | Values captured at a defined time or revision, independent of later changes |

Do not append `Fact`/`Facts`, `Info`, `Data` or `Model` simply because a type carries data. A suffix
needs a domain meaning or an established framework contract: a fact in a rule engine or dimensional
model is meaningful; `OrderFact` as a generic name for an order query result is not.

Do not replace every `Fact` with `Snapshot`. Being a record or read-only DTO does not establish snapshot
semantics. Apply the `Dto` and `Projection` rules below when those distinctions are the actual reason
for a separate shape.

## `Response` is HTTP-only; `Dto` is a deliberate disambiguator

- The `Response` suffix belongs to the **HTTP wire layer** only. It does not belong on the C#
  service/client payloads that adapters pass around: a typed result wrapper is already the
  "did it succeed" envelope, so `Result<XResponse, XError>` double-encodes "this is a reply".
- **Payloads do not mechanically gain or lose `Dto`.** Keep the suffix where it usefully distinguishes a
  data shape from a same-named entity or domain concept (`OrderDto`); omit it where the payload name is
  already unambiguous (`Shipment`, `Refund`, `Invoice`). Accept an SDK name collision and resolve it with
  a `using` alias in the few files that need both types.
- **The entity's own name — bare or `Dto`-suffixed — belongs to the shape that models the entity.**
  Name a partial shape for what it actually is; whether a field belongs to that concept is a question
  about the domain word, never about whether the field is sensitive.

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

`X` is the mapped subject, and one class covers that subject's family — both directions and its parts.
Name it for the family, not for one member of it (`PaymentMappers`, not `PaymentVerificationMappers`).
A name statable only as a category or a location — `Value`, `Common`, `Misc`, the owning module or
layer — is a junk drawer that will collect unrelated subjects; split it by subject.

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
