---
name: seeding
description: The seeding standard for a .NET service — a seeder may only write data production code writes directly, so anything whose only production write path is a handler reacting to an event (read-model projections, event-synced replicas, user rows provisioned on registration, external-provider records, inbox/outbox messages) is never inserted by a seeder; drive the trigger instead. Covers the dev-versus-test seeder split, the producing service's seeding simulator and the dependency direction that makes it work, the two sanctioned exceptions (an integration-test projection seeder driven from the same canonical catalog, and inherently unreproducible historical state), constructor-built seed state with factory `Seed` statics, one canonical seed-state model shared by producer and consumer rather than a `Snapshot` or mirror hierarchy, sentinel guards, and idempotency. Use before writing or changing any seeder, when a table is empty at seed time, when a standalone host lacks another service's data, when a seed-state type would collide on a name with a domain type, or when reviewing a `context.X.AddRange(...)` call.

kind: contract
---

# seeding

The standard is `standards/dotnet/data/SEEDING.md` in `tomjseery/dotagents`, deployed to `~/.agents/standards/dotagents/dotnet/data/SEEDING.md`. Read it and follow it; this skill only routes to it.
