---
name: concurrency
description: EF Core concurrency standard — optimistic concurrency tokens by default with `DbUpdateConcurrencyException` as the expected conflict, multi-row invariants versioned or locked on the aggregate root, pessimistic row locks only for short hard-to-retry transactions, taken as raw SQL in the owning repository in the weakest mode that holds, a fixed lock order, the execution strategy around a locking transaction, and advisory locks named as acquisitions. Use when two writers can race on the same rows, adding a concurrency token, reaching for `FOR UPDATE`/`FOR SHARE`, fencing a delete, or handling `DbUpdateConcurrencyException`.
kind: contract
domain: dotnet
profile: ef-core
applicability: projects using EF Core
requires: ef-core
provenance: library
---

# Concurrency

Read and follow the [canonical definition](../../.agents/efcore/contract/concurrency/SKILL.md) in full.
This discovery entry is generated; edit the referenced `.agents/` definition.
