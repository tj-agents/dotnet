---
name: result-carriers
description: Choosing and using the Reunion Result/Option carriers in a .NET service — the table that picks `Result<TValue, TError>` / `UnitResult<TError>` / `Option<T>` / `T?` / `IReadOnlyList<T>` / plain value from the decisions a caller must make, where each carrier may and may not appear (never in HTTP DTOs, protobuf, events, entities, or config), target-typed construction versus named cases versus factories, observation through `Match`/`TryGetValue` with no throwing accessor, composition with `Map`/`Bind`/`MapError`/`Ensure`/`OrFailure`/`ValueOr`/`Sequence`/`Traverse`, and .NET 11 native-union matching. Use when picking a return type for a new method, converting a nullable to an Option, composing a chain of fallible operations, or reviewing code that reaches for a bool, an enum, or an exception where a Result belongs.
---

# result-carriers

This is a Claude Code compatibility stub. Do not edit skill instructions here.

Read and follow the canonical agent-agnostic skill at ../../../.agents/skills/result-carriers/SKILL.md.
