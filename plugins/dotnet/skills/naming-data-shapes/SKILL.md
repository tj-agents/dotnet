---
name: naming-data-shapes
description: Name C# data shapes by their meaning — when the domain noun stands alone and when a suffix such as Dto, Summary, Snapshot, Projection, Decision, Evidence, Proof, Descriptor, Catalog, Binding or Context carries a real distinction. Use when defining or reviewing a record, DTO, query result or shape shared by application callers.
kind: contract
domain: dotnet
profile: core
applicability: all C# and .NET code
requires: none
provenance: language, house
---

# Data-shape naming

Owns the naming of C# data shapes carried between callers — payloads, summaries, snapshots, projections.

## Applicability

These conventions apply to C# data shapes independently of a persistence library or transport.
Shared identifiers follow `dotnet:naming`. Entity/value identity,
behavior and aggregate boundaries belong to the selected `dotnet:domain-ddd`
contract; value representation and construction belong to
`dotnet:domain-values`. This contract names the data shapes carried between
callers.

## Name what the value represents

Use the established domain noun and add the distinction carried by the shape:

| Meaning | Example |
|---|---|
| An application payload | `Shipment`, `Invoice`, `Address` |
| A summary or details contract | `OrderSummary`, `OrderDetails` |
| A lifecycle state | `OrderStatus` |
| Values captured at a defined instant or revision | `OrderSnapshot` |
| A transfer shape distinguished from the entity of the same subject | `OrderDto` |
| An intermediate query shape awaiting mapping or enrichment | `OrderProjection` |

A snapshot's values represent that captured state independently of later changes. The name follows
that guarantee. A summary or selection remains named for its represented meaning when immutability is
merely its implementation shape.

The entity's domain name, with `Dto` where needed to distinguish it, identifies the shape that models
that entity. A partial shape gets the name of the part it represents. Use the same noun for the same
concept across application and internal module boundaries.

## DTOs describe the application contract

Use `Dto` where it distinguishes a transfer contract from a same-named entity or value. Use the domain
noun alone where the contract is already unambiguous. Keep names stable when the same application shape
is consumed from different transports. Resolve an SDK name collision with a local `using` alias.

Application input types name the accepted operation or reusable input shape. Endpoint-specific naming
and wire shaping follow `dotnet:http-api` for HTTP or
`dotnet:proto` for protobuf. These are selected at the transport boundary.

## Projections describe intermediate query shapes

A repository returning a persisted entity or read model uses that type directly. A repository returning
the final application shape uses that shape's normal name. `Projection` identifies an ephemeral query
shape that its consumer must map or enrich before returning the final contract; keep it internal to
that boundary.

For example, a query can return `OrderSummary` directly. A query returning component values that the
service combines with delivery information can return `OrderProjection`, and the service produces
`OrderDetails`. The distinct name reflects the distinct contract. Storage location alone does not
create a second data shape.

## Decisions, evidence and proofs

Use `Decision` for the verdict an evaluator returns — the outcome plus the diagnostics the caller acts
on, as in ASP.NET Core's `AuthorizationResult`. Use `Evidence` for the input facts gathered to support
that decision, and `Proof` for a value issued only when the check succeeded, carried so a later
operation can require that the check ran instead of re-checking — the vocabulary of
[RFC 9334](https://www.rfc-editor.org/rfc/rfc9334), where evidence is appraised and the appraisal
result is what relying parties consume. One decision family uses one of each, never near-synonyms side
by side.

## Descriptors, catalogs, bindings and contexts

Use `Descriptor` for an immutable metadata record describing a declared thing, keyed by its identity,
as `ServiceDescriptor` describes a service; the described thing lives elsewhere. Use `Catalog` for the
complete authoritative enumeration of a closed set, consumed by enumeration like a database's system
catalog; a keyed lookup populated by registrants is a registry under
`dotnet:naming-collaborators`. Use `Binding` for the bare association between
two declared identities, as a WSDL binding ties an abstract interface to a concrete protocol; a domain
fact with its own granted-and-revoked lifecycle is an assignment. Use `Context` for the current
operation's ambient values assembled at the boundary, like `HttpContext`, with no use-case behaviour;
a conversation that accumulates state over a lifetime is a session.

## Payload shape and operation outcome have separate owners

The shape name states what the value represents; the collaborator method states how it is produced.
`OrderSnapshot` can be read, resolved or sent to a caller without changing its captured-state meaning.
A resolution operation can return that snapshot directly; a separate `Resolution` payload is useful
when the result itself contains distinct resolution information consumed together.

Presence, failure and validation decisions follow their selected result/validation contracts. With
Reunion, an application operation may return `Option<OrderSnapshot>` while `OrderSnapshot` retains its
normal properties. Whole-operation absence and a nullable property inside a DTO represent different
contracts. See `dotnet:errors-carriers` when that profile is selected.
