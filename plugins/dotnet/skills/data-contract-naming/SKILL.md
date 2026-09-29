---
name: data-contract-naming
description: Name C# data contracts by their meaning — domain payloads, summaries, details, statuses, captured snapshots, DTO disambiguation and intermediate projections. Use when defining or reviewing a record, DTO, query result or contract shared by application callers.
kind: contract
domain: dotnet
profile: core
applicability: all C# and .NET code
requires: none
provenance: language, house
---

# Data-contract naming

## Applicability

These conventions apply to C# data shapes independently of a persistence library or transport.
Shared identifiers follow [dotnet:csharp-naming](../csharp-naming/SKILL.md). Domain modeling and value
invariants follow the selected [dotnet:ddd](../ddd/SKILL.md) and
[dotnet:value-semantics](../value-semantics/SKILL.md) contracts.

## Name what the value represents

Use the established domain noun and add the distinction carried by the shape:

| Meaning | Example |
|---|---|
| The domain payload | `Shipment`, `Invoice`, `Address` |
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
and wire shaping follow [dotnet:http-api](../http-api/SKILL.md) for HTTP or
[dotnet:proto](../proto/SKILL.md) for protobuf. These are selected at the transport boundary.

## Projections describe intermediate query shapes

A repository returning a persisted entity or read model uses that type directly. A repository returning
the final application shape uses that shape's normal name. `Projection` identifies an ephemeral query
shape that its consumer must map or enrich before returning the final contract; keep it internal to
that boundary.

For example, a query can return `OrderSummary` directly. A query returning component values that the
service combines with delivery information can return `OrderProjection`, and the service produces
`OrderDetails`. The distinct name reflects the distinct contract. Storage location alone does not
create a second data shape.
