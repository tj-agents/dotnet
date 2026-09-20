---
name: keyed-strategies
description: The standard shape for behaviour that varies by a closed key in a .NET service — one module-local generic factory owning keyed DI resolution, operation-specific named facades that delegate through it, a registration builder that declares every family vertically and rejects duplicate keys, incomplete coverage and conflicting lifetimes so adding an enum member fails composition, the type-hierarchy half for branches DI cannot reach (an ORM-materialised entity, where the persistence discriminator is the key), matching a shared concern as a capability rather than by the key, and the anti-patterns it replaces (branching on the key inside key-agnostic code, service location outside the factory, parallel hand-written maps, returning an enum every caller re-switches on, throwaway result records, discard-tuple calls). Its sibling is `keyed-unions`, for variants that do not share one signature. Use when behaviour differs per enum/discriminator value, when adding a value to such an enum, when tempted to write a `switch` on a type/kind/mode key, when the branch sits in an entity the container cannot reach, when a concern spans some keys but not all, or when reviewing keyed DI registrations.
kind: contract
domain: dotnet
profile: keyed-design
applicability: closed-key behaviour selected through keyed dependency injection
requires: microsoft-extensions-dependency-injection
provenance: framework, pattern, house
---

# Keyed strategies

Read and follow the [canonical shared definition](../../../.agents/contract/keyed-strategies/SKILL.md) in full.
This discovery entry is generated; edit the referenced `.agents/` definition.
