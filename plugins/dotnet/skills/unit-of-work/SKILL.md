---
name: unit-of-work
description: The unit of work for a .NET service, independent of an ORM — repositories and the outbox stage changes, the use case commits once through `IUnitOfWork.SaveChangesAsync`, `ExecuteAsync` runs caller-supplied work inside the transaction envelope, and one unit of work covers one service's database. Use when committing, opening a transaction, wrapping work in a retry or transaction envelope, or deciding who saves.
kind: contract
domain: dotnet
profile: core
applicability: C# projects that persist state, regardless of persistence library
requires: none
provenance: pattern, house
---

# Unit of work

Read and follow the [canonical definition](../../.agents/dotnet/contract/unit-of-work/SKILL.md) in full.
This discovery entry is generated; edit the referenced `.agents/` definition.
