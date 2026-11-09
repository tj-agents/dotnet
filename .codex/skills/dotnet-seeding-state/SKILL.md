---
name: seeding-state
description: How a .NET seeder's seed state is built — a constructor-built singleton with get-only properties built from compile-time-deterministic inputs, and per-aggregate factory `Seed` statics chaining a reflection `With(nameof(X.Id), id)` over the real `Create` method, then clearing the resulting domain events. Covers one canonical seed-state model shared by producer and consumer, never a `Snapshot` or mirror hierarchy, plus idempotency and sentinel guards. Use when writing seed state, when a seed-state type collides on a name with a domain type, or reviewing a seeder's existence guard.
kind: contract
domain: dotnet
profile: seeding
applicability: .NET projects with development or test seeders
requires: seeding
provenance: library, house
---

# Seeding state

Read and follow the [canonical definition](../../../.agents/dotnet/contract/seeding/state/SKILL.md) in full.
This discovery entry is generated; edit the referenced `.agents/` definition.
