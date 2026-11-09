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

Owns how seed state is built: constructor-built seed state, factory `Seed` statics, one canonical model, and idempotency.

```text
Need:   a seeded Order with a fixed id.
Write:  OrderFactory.Seed(OrderIds.First, customer, total), which chains With(nameof(Order.Id), id)
        over Order.Create and then clears the domain events.
Never:  a Seed static on Order itself, or a seeder assigning to seed state.
```

`Seed` chains a reflection `With(nameof(Order.Id), id)` over the real `Create` method so every invariant
`Create` enforces still runs, then clears the resulting domain events to suppress outbox publication. A
seeder reads `OrderFactory.Seed(...)` and persists the result; it never builds the entity itself. See
`dotnet:seeding-scope` for what a seeder may persist in the first place.

## Seed state is constructor-built; seeders only persist

Seed state is a singleton with a parameterless constructor that builds every entity it exposes from
compile-time-deterministic inputs — ids from a shared identity source, geometry, addresses, names, and
relationships fixed in the constructor. All properties are get-only; there are no setters.

Per-aggregate `XFactory.Seed` statics live with the domain's factories and chain a reflection `With(nameof(X.Id),
id)` over the domain's real `Create` method, so invariants are enforced, then clear the resulting domain events
to suppress outbox publication. **A domain entity never carries a `Seed` static itself** — that leaks test and
infrastructure concerns into the domain; it goes on the factory.

Seeders read from seed state and persist. They never assign to it. The EF Core persistence example is owned by
`efcore:persistence`; the same ownership rule applies to other persistence implementations.

## One canonical seed-state model

Producer and consumer share **one** seed-state type: the seeder builds it, the fixture exposes it, the test
reads it, so "the confirmed booking" means the same thing at every hop. This is the same type a producer's
seeding simulator publishes from, under `dotnet:seeding-scope`.

Where that type and a domain type would otherwise collide on a name, **namespace separation is the answer** —
they live in different namespaces and a `using` alias disambiguates the one file needing both. Never introduce
a `Snapshot`, `Source`, mirror, adapter or wrapper type to dodge a collision. A parallel hierarchy has to be
updated in lockstep with the real one, silently drifts when it is not, and the test's expectation then no
longer describes what was actually seeded.

## Idempotency and sentinel guards

Every dev seeder must be safe to run repeatedly against a database that already holds seed data — use a
seed-if-empty helper for bulk inserts, or guard individual rows with an existence check.

**Where a cross-service event handler can write to the same table before the seeder runs, do not guard on
whole-table existence** — one race-created row would skip the entire seed. Guard on a specific entity only the
seeder ever creates, so partial event-driven rows cannot suppress a full seed. See `dotnet:seeding-scope` for
which rows a seeder may create in the first place.
