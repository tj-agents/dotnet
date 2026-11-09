---
name: seeding-scope
description: A seeder may only write data production code writes directly — anything whose only production write path is a handler reacting to an event (read-model projections, event-synced replicas, registration-created user rows, external-provider records, inbox/outbox messages) is never inserted; drive the trigger instead. Covers the dev-versus-test split, the producing service's seeding simulator, and the two sanctioned exceptions. Use before writing or changing any seeder, when a table is empty at seed time, or reviewing a `context.X.AddRange(...)` call.
kind: contract
domain: dotnet
profile: seeding
applicability: .NET projects with development or test seeders
requires: seeding
provenance: library, house
---

# Seeding scope

Owns what a seeder may and may not write directly, the dev/test split, seeding simulators and the sanctioned exceptions.

```csharp
public sealed class OrderSeedSimulator
{
    private readonly IIntegrationEventPublisher integrationEventPublisher;
    private readonly OrderSeedState seedState;

    public OrderSeedSimulator(IIntegrationEventPublisher integrationEventPublisher, OrderSeedState seedState)
    {
        this.integrationEventPublisher = integrationEventPublisher;
        this.seedState = seedState;
    }

    public Task SeedAsync(CancellationToken ct = default) =>
        integrationEventPublisher.PublishAsync(seedState.OrderCreated, ct);
}
```

`OrderSeedState` is the producer's canonical seed catalog, owned by `dotnet:seeding-state`; `OrderCreated`
is its integration event. The simulator drives the consumer's normal handler path instead of inserting its
projection rows.

## Applicability

This contract applies to .NET development and test seeders regardless of persistence library. It requires `seeding`. EF Core persistence details belong to `efcore:persistence`. Installing `dotnet@tj-agents` makes this guidance available; it does not select those technologies for a consuming repository.

> ## ⚠ Read this before writing a seeder body
>
> **Never write `context.X.Add(...)` or `context.X.AddRange(...)` against storage whose entity is only
> written by a handler.**
>
> **The rule: a seeder may only write data that production code writes directly.** If production creates the
> data as a *reaction* — to an event, an outbox message, a handler firing, a webhook — the seeder must drive
> that same trigger, not bypass it and write the row.

## What is never seeded directly

Each of these has a production write path that is only ever a reaction:

- **Read-model projections and event-synced replicas** — anything a `XChangedEvent` handler writes,
  including a replica named `*Entity` since it is the only model of that concept in its own service. The rule
  follows from how the row is written, not the type suffix.
- **User rows** created by a handler reacting to a registration event from the identity service.
- **Profile or membership rows** alongside those users, or from an invitation-accept flow. Only a founding
  owner membership seeds alongside its own aggregate; anything from an accepted invitation does not.
- **External-provider records** — payout accounts, customer records, anything provisioned by a handler.
- **Inbox, outbox, and messaging rows** — owned by the messaging infrastructure.
- **Anything else whose only production write sits inside an integration- or domain-event handler, an outbox
  dispatcher, or a webhook handler.**

**An empty table at seed time is not a defect** — the event has not been processed yet.

**The check, before writing the body:** open the entity's repository, service, or handler. If the only
production `.Add`/`.AddRange` call on that storage sits inside an event handler, the seeder may not write it
either — make the trigger fire.

## Dev seeder versus test seeder

- A **dev seeder** runs in development and E2E environments via the host's database initializer.
- A **test seeder** runs in integration tests only — never in E2E or dev startup.

Never confuse them: **if an E2E fixture lacks data, the fix is always in a dev seeder.**

## A standalone host gets the producing service's simulator, not a projection insert

A service run standalone still needs the projection data it would receive in production. Without the producer
running, its consumer's projection tables stay empty, the UI shows nothing, and dependent E2E scenarios fail.
The approved mechanism is a **seeding simulator**: a small worker host, owned by the **producing** service, that
publishes its canonical integration events on startup and exits. The consumer's projection handlers then run
unchanged — same code path, same data shape, in both scenarios.

- The producer owns a **seed contracts** package of canonical event records, built from the seed state
  `dotnet:seeding-state` owns, so its seeders and the simulator derive from one source and cannot drift.
- The simulator is registered as a resource in the **consumer's** standalone host, and not in an umbrella host
  where the real producer is already present.

**Dependency direction is the part people get wrong.** A producer's seed-contracts package is referenced **by**
its consumers and references **none** of them. A simulator belongs only to a **data service whose peers do not
run** — never an agnostic adapter service, which owns no seed catalog and no simulator.

## The two sanctioned exceptions

**1. An integration-test projection seeder.** Booting the producer's bus and handlers inside a test host is slow
and flaky, so a read-model module may ship an `XProjectionTestSeeder` that direct-inserts the read-model rows.
Safe only because all three hold:

- it is driven from the **same canonical seed catalog** that drives the dev/E2E simulator, so the inserted rows
  are byte-identical to what the handler path would produce — there is no second source of truth to drift from;
- it is a **test** seeder, so dev and E2E keep the simulator → event → projection-handler path unchanged;
- it maps each spec through the same `Create(...)` call, field for field, exactly as the handler does.

Test code still never calls `db.XReadModels.Add(...)` itself; it reaches for seed-state handles — for read
models, the catalog specs, never the read-model entities.

**2. Inherently unreproducible historical state.** The "drive the trigger" rule assumes the trigger *can* be
replayed at seed time. A narrow class fails that assumption: state whose only producer is an event that can no
longer fire — historical sales against a date already passed, where the real provider only emits on a live
webhook and the transaction cannot be re-made. There, reflection-seeding the derived row directly is the right
tool, **not** a simulator faking the trigger. Each consumer seeds its own copy; nothing crosses the boundary.

This is the **only** sanctioned reason to reflection-seed handler-owned state outside integration tests. Do not
generalize it to live or future state, which still goes through the event path.
