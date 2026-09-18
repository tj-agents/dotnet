# Seeding

> ## ⚠ Read this before writing a seeder body
>
> **Never write `context.X.Add(...)` or `context.X.AddRange(...)` against a DbSet whose entity is only written
> by a handler in production.**
>
> **The rule: a seeder may only write data that production code writes directly.** If production creates the
> data as a *reaction* — to an event, an outbox message, a handler firing, a webhook — the seeder must drive
> that same trigger, not bypass it and write the row.

## What is never seeded directly

Each of these has a production write path that is only ever a reaction:

- **Read-model projections and event-synced replicas.** Anything written by a `XChangedEvent` handler —
  including a replica named `*Entity` because it is the only model of that concept in its own service. The rule
  follows from *how the rows are written*, not from the type suffix.
- **User rows** created by a handler reacting to a registration event from the identity service.
- **Profile or membership rows** written alongside those users, or written by an invitation-accept flow. Only a
  founding owner membership is seeded, alongside its own aggregate; anything derived from an accepted invitation
  is not.
- **External-provider records** — payout accounts, customer records, anything provisioned by a handler.
- **Inbox, outbox, and messaging rows** — owned by the messaging infrastructure.
- **Anything else whose only production write sits inside an integration- or domain-event handler, an outbox
  dispatcher, or a webhook handler.**

**An empty table at seed time is not a defect.** It means the event has not been processed yet, which is correct
and expected.

**The check, before writing the body:** open the entity's repository, service, or handler. If the only production
code calling `.Add`/`.AddRange` on that DbSet is inside a handler reacting to an event, the seeder may not write
it either — make the trigger fire.

## Dev seeder versus test seeder

- A **dev seeder** runs in development and E2E environments through the host's database initializer.
- A **test seeder** runs in integration tests only — never in E2E or dev startup.

Never confuse them: **if an E2E fixture is missing data, the fix is always in a dev seeder.**

## A standalone host gets the producing service's simulator, not a projection insert

A service run standalone still needs the projection data it would receive in production. Without the producer
running, its consumer's projection tables stay empty, the UI shows nothing, and dependent E2E scenarios fail.
The approved mechanism is a **seeding simulator**: a small worker host, owned by the **producing** service, that
publishes its canonical integration events on startup and exits. The consumer's projection handlers then run
unchanged — same code path, same data shape, in both scenarios.

- The producer owns a **seed contracts** package holding the canonical event records, so its own seeders and the
  simulator derive from one source and cannot drift field-by-field.
- The simulator is registered as a resource in the **consumer's** standalone host, and not in an umbrella host
  where the real producer is already present.

**Dependency direction is the part people get wrong.** A producer's seed-contracts package is referenced **by**
its consumers and references **none** of them. A simulator is owned only by a **data service whose peers do not
run** — never by an agnostic adapter service. An adapter that always runs owns no seed catalog and no simulator,
and parking a catalog of a consumer's domain semantics inside an agnostic adapter is wrong for the same reason.

## The two sanctioned exceptions

**1. An integration-test projection seeder.** Booting the producer's bus and handler path inside a test host is
slow and flaky, so each read-model module may ship an `XProjectionTestSeeder` that direct-inserts the read-model
rows. This is safe only because all three hold:

- it is driven from the **same canonical seed catalog** that drives the dev/E2E simulator, so the inserted rows
  are byte-identical to what the handler path would produce — there is no second source of truth to drift from;
- it is a **test** seeder, so dev and E2E keep the simulator → event → projection-handler path unchanged;
- it maps each spec through the same `Create(...)` call, field for field, exactly as the handler does.

Test code still never calls `db.XReadModels.Add(...)` itself. Tests reach for seed-state handles, and for read
models those handles are the catalog specs, never the read-model entities.

**2. Inherently unreproducible historical state.** The "drive the trigger" rule assumes the production trigger
*can* be replayed at seed time. A narrow class of data fails that assumption: state whose only producer is an
event that can no longer fire for the data in question — historical sales against a date that has already
passed, where the real provider only emits on a live webhook and the transaction cannot be re-made. There,
reflection-seeding the derived row directly is the right tool, **not** a simulator faking the trigger. Each
consumer seeds its own copy on its own side; nothing crosses the boundary.

This is the **only** sanctioned reason to reflection-seed handler-owned state outside integration tests. Do not
generalize it to live or future state, which still goes through the event path.

## Seed state is constructor-built; seeders only persist

Seed state is a singleton with a parameterless constructor that builds every entity it exposes from
compile-time-deterministic inputs — ids from a shared identity source, geometry, addresses, names, and
relationships fixed in the constructor. All properties are get-only; there are no setters.

Per-aggregate `XFactory.Seed` statics live with the domain's factories and chain a reflection `With(nameof(X.Id),
id)` over the domain's real `Create` method, so invariants are enforced, then clear the resulting domain events
to suppress outbox publication. **A domain entity never carries a `Seed` static itself** — that leaks test and
infrastructure concerns into the domain; it goes on the factory.

Seeders read from seed state and persist. They never assign to it:

```csharp
public async Task SeedAsync(CancellationToken ct)
{
    if (await context.Warehouses.AnyAsync(ct)) return;
    context.Warehouses.AddRange(seedData.Warehouses);
    await context.SaveChangesAsync(ct);
}
```

## One canonical seed-state model

Producer and consumer share **one** seed-state type: the seeder builds it, the fixture exposes it, the test
reads it, so "the confirmed booking" means the same thing at every hop.

Where that type and a domain type would otherwise collide on a name, **namespace separation is the answer** —
they live in different namespaces and a `using` alias disambiguates the one file needing both. Never introduce
a `Snapshot`, `Source`, mirror, adapter or wrapper type to dodge a collision. A parallel hierarchy has to be
updated in lockstep with the real one, silently drifts when it is not, and the test's expectation then no
longer describes what was actually seeded.

## Idempotency and sentinel guards

Every dev seeder must be safe to run repeatedly against a database that already holds seed data — use a
seed-if-empty helper for bulk inserts, or guard individual rows with an existence check.

**Where a cross-service event handler can write to the same table before the seeder runs, do not guard on
`AnyAsync()`** — one race-created row would skip the entire seed. Guard on a specific entity only the seeder ever
creates, so partial event-driven rows cannot suppress a full seed.
