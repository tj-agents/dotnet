---
name: value-semantics
description: The pattern for a small immutable value and its construction — choosing a `readonly record struct` against a reference value object on the `default(T)` and allocation-volume tests, putting construction and the value's own behaviour on the type as a static `From` or `TryGet…` rather than in helpers beside it, and the shape a `Try` method follows. Use when introducing a type to carry a value, when a method returns several related values, when deciding between a struct and a class for one, or when reviewing a `Try` signature.
kind: contract
domain: dotnet
profile: patterns
applicability: all C# and .NET code
requires: none
provenance: language, pattern, house
---

# Value semantics and construction

Read and follow the [canonical shared definition](../../../.agents/contract/value-semantics/SKILL.md) in full.
This discovery entry is generated; edit the referenced `.agents/` definition.
