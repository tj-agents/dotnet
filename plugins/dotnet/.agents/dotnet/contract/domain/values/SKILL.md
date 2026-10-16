---
name: domain-values
description: The pattern for a small immutable value and its construction — defaulting to a reference record and choosing a `readonly record struct` only when its default is valid, it is not optional/nullable, and allocation volume matters, putting construction and the value's own behaviour on the type as a static `From`/`Create`/`TryGet…` rather than in helpers beside it, and the shape a `Try` method follows. Use when introducing a type to carry a value, when a method returns several related values, when deciding between a struct and a class for one, or when reviewing a `Try` signature.
kind: contract
domain: dotnet
profile: patterns
applicability: all C# and .NET code
requires: none
provenance: language, pattern, house
---

# Value semantics and construction

Owns small immutable value representation and construction — struct-or-class choice, factories, `Try`.

## Applicability

This contract applies to every C#/.NET repository and has no application-stack prerequisite.

## Struct or reference

Default to a reference record, preferably a `sealed record`, for a small immutable value object or
multi-value result. Use a `readonly record struct` only when `default(T)` is genuinely valid, the value is
not held as optional/nullable, and allocation volume matters (per item of a materialised collection or
on a hot path). Keep construction private when ordinary creation canonicalizes the value.

## Construction belongs on the type

Give the type a static factory and let it carry its own behaviour: `From` converts an existing external
shape (a row, a DTO, a raw string), `Create` builds directly from the value's own constituent parts, and
`TryGet…` covers either when construction can fail. A helper that builds or compares the value from
outside splits one concept across two places.

## A `Try` method follows the BCL shape

A method named `Try…` returns `bool` and yields its result through one `out` parameter, named
`TryGet<Thing>` when it fetches one. Annotate a reference-typed result `[MaybeNullWhen(false)]` and an
input guard `[NotNullWhen(true)]`. Several values out is one named type chosen by the representation rule
above, never several `out` parameters or a tuple.

This is a deliberate, narrow exception to `errors-carriers`' bool table, not a second way to spell the
same choice: reach for `Try` only where it mirrors an existing BCL member (`int.TryParse`-shaped), sits on
a hot path where allocating a `Result` is the actual cost, and has no error value worth a caller branching
on — the moment a caller needs to know *why* the lookup failed, return an `Option<T>` or `Result` instead.
