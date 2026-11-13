---
name: mapping
description: Use when designing C# conversions, mapper families or receiver-owned extensions, including extension-block syntax and pure-query boundaries.
kind: contract
domain: dotnet
profile: core
applicability: all C# and .NET code
requires: none
provenance: language, house
---

# Mapping and extensions

Owns C# type-conversion and receiver-owned pure-operation naming — mapper families and extensions.

## Applicability

These conventions apply to C# type conversions and receiver-owned pure operations. Shared identifiers
follow `dotnet:naming`, and result shapes follow `dotnet:dtos`.

## A subject owns its mapping family

Place type-to-type conversions in a static `XMappers` class with extension methods named for the target.
`X` is the mapped subject and covers its related shapes and both directions: `PaymentMappers` owns the
payment mapping family. Each family has one source owner. Consumers call its conversions directly.
`X` is the subject, never a payload word: the family producing `ShipmentDto` is `ShipmentMappers`, not
`ShipmentDtoMappers`, and an injected mapper producing it is a `ShipmentMapper`, not a `ShipmentDtoMapper`.
A type-to-type conversion is a mapping-family member, never a `Create` on the target contract: a pure data
payload has no invariant to guard, and a `Create` that knows the source type leaks mapping into the contract.

```csharp
internal static class ShipmentMappers
{
    extension(ShipmentEntity entity)
    {
        public Shipment ToShipment() => new(entity.Id, entity.TrackingReference);
    }
}
```

Use the extension syntax supported by the project's language version. Keep asynchronous data loading and
use-case orchestration with their respective collaborators; pass the resulting inputs to the pure
conversion.

## New extension members go in `extension()` blocks

All ordinary extension members use `extension(Receiver)` blocks — the C# 14 unified form, which also
covers properties, indexers, and static members and groups them by receiver. Keep receiver-owned members
in one `XExtensions` static class; an `XMappers` mapping family may hold one block per related receiver.
Do not add a new legacy `public static … (this X x)` method.

When you edit an existing extension container, migrate every ordinary member in it, so that no class ever
mixes `extension()` blocks with legacy `this` parameters. A container left untouched stays legacy until
its own sweep — track that as tech debt rather than half-migrating a class.

The one exception is a declaration contract that genuinely requires the receiver in the method signature,
such as a source-generated `[LoggerMessage]` partial method; see `dotnet:logging`.

## Pure conversions and queries use receiver extensions

A pure conversion or derived query with one clear receiver lives with its related operations in `XExtensions`,
or in its mapping family when it is a conversion. Examples are `value.ToDto()`,
`reading.ToNormalized()` and `state.IsTerminal()`. Use the shortest unambiguous domain name at the call
site. For intrinsic domain behavior and value construction, select the owner through
`dotnet:domain-ddd` when DDD applies and
`dotnet:domain-values`.

## Choose conversion mechanics for the data

Use an exhaustive switch for a small closed enum conversion. Use a `FrozenDictionary` or `FrozenSet`
for a deterministic data table whose entries are clearer to inspect as data, such as provider-status
normalization or legal transition edges. Use conditional logic where the outcome depends on contextual
validation or calculation. Behavior selected by a closed key follows
`dotnet:keyed-strategies` when that pattern is selected.
