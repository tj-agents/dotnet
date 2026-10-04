---
name: naming-mapping
description: C# mapping and extension conventions — subject-owned XMappers families, target-named conversions, receiver-owned XExtensions and choosing an exhaustive conversion or a data lookup. Use when mapping between types, naming mapping methods or locating pure conversion logic.
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
follow `dotnet:naming`, and result shapes follow
`dotnet:naming-dtos`.

## A subject owns its mapping family

Place type-to-type conversions in a static `XMappers` class with extension methods named for the target.
`X` is the mapped subject and covers its related shapes and both directions: `PaymentMappers` owns the
payment mapping family. Each family has one source owner. Consumers call its conversions directly.

```csharp
internal static class ShipmentMappers
{
    extension(ShipmentEntity entity)
    {
        public Shipment ToShipment() => new(entity.Id, entity.TrackingReference);
    }
}
```

Use the extension syntax supported by the project's language version; syntax and field conventions
belong to `dotnet:style`. Keep asynchronous data loading and use-case
orchestration with their respective collaborators; pass the resulting inputs to the pure conversion.

## Pure conversions and queries use receiver extensions

A pure conversion or derived query with one clear receiver lives with its related operations in `XExtensions`,
or in its mapping family when it is a conversion. Examples are `value.ToDto()`,
`reading.ToNormalized()` and `state.IsTerminal()`. Use the shortest unambiguous domain name at the call
site. For intrinsic domain behavior and value construction, select the owner through
`dotnet:domain-ddd` when DDD applies and
`dotnet:domain-values`. A separate decision over independent peer inputs
follows the collaborator convention in `dotnet:naming-collaborators`.

## Choose conversion mechanics for the data

Use an exhaustive switch for a small closed enum conversion. Use a `FrozenDictionary` or `FrozenSet`
for a deterministic data table whose entries are clearer to inspect as data, such as provider-status
normalization or legal transition edges. Use conditional logic where the outcome depends on contextual
validation or calculation. Behavior selected by a closed key follows
`dotnet:keyed-strategies` when that pattern is selected.
