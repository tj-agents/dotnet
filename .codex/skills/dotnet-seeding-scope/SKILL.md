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

Read and follow the [canonical definition](../../../.agents/dotnet/contract/seeding/scope/SKILL.md) in full.
This discovery entry is generated; edit the referenced `.agents/` definition.
