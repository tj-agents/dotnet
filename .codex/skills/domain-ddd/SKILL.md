---
name: domain-ddd
description: Domain-driven design's building-block vocabulary for a .NET domain model — the entity/value-object split by identity, equality, and lifecycle (an entity's own behaviour lives here; a value object's reference record default and tests that justify a struct are the `domain-values` contract's job), the aggregate as the transactional consistency boundary with a root-only external reference rule, an aggregate announcing its own state change through a domain event (owned by the `domain-events` contract), domain services for business operations without a natural entity/value owner and their boundary with application orchestration, and the anti-patterns — an anemic model whose rules leaked into an application service, a God aggregate, and an invariant enforced by reaching across an aggregate boundary. Use when designing a domain type, deciding whether something is an entity or a value object, drawing or crossing an aggregate boundary, or reviewing a domain model for behaviour that belongs on a type but lives in a service instead.
kind: contract
domain: dotnet
profile: domain-model
applicability: domain models designed with DDD building blocks (entities, value objects, aggregates)
requires: domain-model-architecture
provenance: architecture, pattern, house
---

# Domain-driven design — entities, value objects, and aggregates

Read and follow the [canonical definition](../../../.agents/dotnet/contract/domain/ddd/SKILL.md) in full.
This discovery entry is generated; edit the referenced `.agents/` definition.
