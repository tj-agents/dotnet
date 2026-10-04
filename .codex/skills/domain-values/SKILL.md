---
name: domain-values
description: The pattern for a small immutable value and its construction — choosing a `readonly record struct` against a reference value object on the `default(T)` and allocation-volume tests, putting construction and the value's own behaviour on the type as a static `From`/`Create`/`TryGet…` rather than in helpers beside it, and the shape a `Try` method follows. Use when introducing or reviewing a type that carries a value, when a method returns several related values, when deciding between a struct and a class for one, or when reviewing a `Try` signature.
kind: contract
domain: dotnet
profile: patterns
applicability: all C# and .NET code
requires: none
provenance: language, pattern, house
---

# Value semantics and construction

Read and follow the [canonical definition](../../../.agents/dotnet/contract/domain/values/SKILL.md) in full.
This discovery entry is generated; edit the referenced `.agents/` definition.
