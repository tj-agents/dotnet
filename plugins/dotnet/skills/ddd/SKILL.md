---
name: ddd
description: Domain-driven design's building-block vocabulary for a .NET domain model — the entity/value-object split by identity, equality, and lifecycle (an entity's own behaviour lives here; a value object's struct-or-class mechanics are the `value-semantics` contract's job), the aggregate as the transactional consistency boundary with a root-only external reference rule, an aggregate announcing its own state change through a domain event (owned by the `domain-events` contract), and the anti-patterns — an anemic model whose rules leaked into an application service, a God aggregate, and an invariant enforced by reaching across an aggregate boundary. Use when designing a domain type, deciding whether something is an entity or a value object, drawing or crossing an aggregate boundary, or reviewing a domain model for behaviour that belongs on a type but lives in a service instead.
kind: contract
domain: dotnet
profile: domain-model
applicability: domain models designed with DDD building blocks (entities, value objects, aggregates)
requires: domain-model-architecture
provenance: architecture, pattern, house
---

# Domain-driven design — entities, value objects, and aggregates

## Applicability

This contract applies only to domain models designed with DDD building blocks. It requires
`domain-model-architecture`. Installing `dotnet@dotagents` makes this guidance available; it does not
select that architecture for a consuming repository.

## An entity has identity; a value object has none

An **entity** is compared and tracked by an id that outlives every change to its other fields — two
entities with identical fields but different ids are different entities. It owns behaviour: a domain
method changes its own state, not a public setter another layer drives from outside.

A **value object** is compared and equal by its fields alone, has no independent lifecycle, and is
replaced rather than mutated. Deciding *that* something is a value — an amount, a range, a version, a
coordinate — is this contract's call. Deciding *how* to build it — `readonly record struct` against a
reference type, construction, a `Try` accessor — is the `value-semantics` contract's job.

## An aggregate is the transactional consistency boundary

An aggregate is one root entity plus the entities and value objects that only make sense attached to it.
The root is the only member another aggregate, module, or caller may hold a reference to; everything else
inside the boundary is reached through the root, never loaded or saved on its own.

Reference another aggregate by its primitive id, never a navigation property — even from inside the same
module. A save that spans two aggregates in one transaction is usually two aggregates that should be one,
or a domain event that should carry the second half of the work instead.

Put an invariant on the aggregate that owns every field it constrains. A rule that reads two aggregates'
state to validate one of them has no single owner and drifts the moment either changes independently.

## A state change worth telling the rest of the system about is a domain event

An aggregate that changes state something else needs to react to **raises** an event; it does not call
out to publish one itself. Raising, dispatching, and translating that event into an integration event is
the `domain-events` contract.

## Anti-patterns

- **An anemic domain model.** Public getters and setters with no domain methods push every rule into an
  application service, which can now construct any state the entity's own methods would have rejected.
  The service becomes the real domain layer and the entity is a data bag it operates on.
- **A God aggregate.** Pulling every related entity into one aggregate because they are all "related"
  produces a boundary nothing can save or lock cheaply. Split until each aggregate has one reason to
  change and one invariant it alone enforces.
- **Reaching across an aggregate boundary to validate.** Fetching a second aggregate inside a method on
  the first, to check a rule that belongs to neither alone, means the invariant has no owner. Model it as
  a domain service, or accept it as an eventually-consistent rule enforced by a domain event handler.
