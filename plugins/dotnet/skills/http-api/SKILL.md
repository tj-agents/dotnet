---
name: http-api
description: HTTP contract standard for a .NET service — services return application DTOs and never HTTP-flavoured `Response` types, controllers return the DTO verbatim by default and a dedicated `Response` only where the wire shape genuinely differs or a public anonymous surface needs a frozen contract, write inputs are `Request` records with `{ get; init; }` and identity taken from the route rather than the body, a single shared request type until create and update contracts diverge, and translating a domain term into its product/API vocabulary exactly once at the Api layer. Use when adding or changing an endpoint, deciding whether a DTO needs a Response wrapper, shaping a write payload, or naming a route.
kind: contract
domain: dotnet
profile: aspnet
applicability: ASP.NET Core HTTP APIs
requires: aspnet-core
provenance: framework, house
---

# HTTP API contracts

Owns the HTTP contract shape — DTO vs Response, write-input `Request` records, route vocabulary.

## Applicability

This contract applies only to ASP.NET Core HTTP APIs. It requires `aspnet-core`. Installing `dotnet@dotagents` makes this guidance available; it does not select those technologies for a consuming repository.

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
same-named entity. Payload conventions belong to
`dotnet:naming-payloads`. HTTP `Request` and `Response`
names describe the boundary contracts defined here; the application keeps its domain-shaped payloads.

## Write inputs are `Request` records

Service write inputs are `Request` types in the application layer — **never the read DTO**, which carries
server-owned fields (`Id`, `UserId`) a caller must not set. Identity comes from the route or method
parameter, not from the body. Request records use `{ get; init; }`.

Where create and update accept the identical writable shape, share **one** `XRequest` rather than duplicating
`CreateXRequest`/`UpdateXRequest`; split them the moment the contracts diverge.

Which validator shape a request gets, and whether it is auto-validated or injected, is the `validation`
skill's subject.

## Idempotency is an API-boundary concern

Use the vocabulary of the IETF
[`Idempotency-Key` draft](https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/)
(expired, but the de facto industry term —
[Stripe's idempotent requests](https://docs.stripe.com/api/idempotent_requests) use the same model). The
client sends an `Idempotency-Key` header carrying a UUID; the server derives a fingerprint from the
payload and stores the `IdempotencyKey` itself — key, fingerprint, outcome — with no `Record`, `Receipt`
or `Command` noun. A missing key on an endpoint that requires one is `400`; the same key with a
different fingerprint is `422`; a retry while the original is still processing is `409`; a completed
request replays its stored outcome. The key stays at the API boundary — domain and application
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
