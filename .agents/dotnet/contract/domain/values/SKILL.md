---
name: domain-values
description: The pattern for a small immutable value and its construction — choosing a `readonly record struct` against a reference value object on the `default(T)` and allocation-volume tests, putting construction and the value's own behaviour on the type as a static `From`/`Create`/`TryGet…` rather than in helpers beside it, and the shape a `Try` method follows. Use when introducing a type to carry a value, when a method returns several related values, when deciding between a struct and a class for one, or when reviewing a `Try` signature.
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

Use a `readonly record struct` for a small immutable value whose identity is entirely its fields when
`default(T)` is valid or harmless. Keep construction private when ordinary creation canonicalizes the
value, but remember that every struct still has an all-default value; reject that value at the consuming
invariant boundary when it is merely harmless. If an invalid default must be impossible to represent, use
a reference value object instead.

Allocation volume is a reason on its own. Prefer the struct where one is created per item of a
materialised collection rather than a handful.

## Construction belongs on the type

Give the type a static factory and let it carry its own behaviour: `From` converts an existing external
shape (a row, a DTO, a raw string), `Create` builds directly from the value's own constituent parts, and
`TryGet…` covers either when construction can fail. A helper that builds or compares the value from
outside splits one concept across two places.

## A `Try` method follows the BCL shape

A method named `Try…` returns `bool` and yields its result through one `out` parameter, named
`TryGet<Thing>` when it fetches one. Annotate a reference-typed result `[MaybeNullWhen(false)]` and an
input guard `[NotNullWhen(true)]`. Several values out is one `readonly record struct`, never several
`out` parameters or a tuple.

This is a deliberate, narrow exception to `errors-carriers`' bool table, not a second way to spell the
same choice: reach for `Try` only where it mirrors an existing BCL member (`int.TryParse`-shaped), sits on
a hot path where allocating a `Result` is the actual cost, and has no error value worth a caller branching
on — the moment a caller needs to know *why* the lookup failed, return an `Option<T>` or `Result` instead.
