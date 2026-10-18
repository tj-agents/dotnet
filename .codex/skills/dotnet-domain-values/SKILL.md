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

Read and follow the [canonical definition](../../../.agents/dotnet/contract/domain/values/SKILL.md) in full.
This discovery entry is generated; edit the referenced `.agents/` definition.
