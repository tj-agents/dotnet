---
name: domain-design
description: Tommy's agreed .NET domain design — entities, value objects, aggregates and domain services. Read before designing or reviewing a domain model; the DDD building-block vocabulary, value construction and domain events are its family members.
kind: contract
domain: dotnet
profile: core
applicability: .NET projects
requires: dotnet
provenance: house
---

# Domain design

```text
Task: Raise OrderCancelledDomainEvent from Order.Cancel.
Load: dotnet:domain-events.

Task: Dispatch those events through an EF Core SaveChanges interceptor.
Load: dotnet:domain-events and efcore:event-dispatch.
```

The first task concerns the domain's announcement; the second selects the EF persistence adapter.
This routing example adds no entity/aggregate design convention.

Owns domain-model design — entities, values, aggregates and domain services.

DDD's building-block vocabulary is `dotnet:domain-ddd` when a project selects that
architecture; value construction is `dotnet:domain-values`; domain events
are `dotnet:domain-events`; EF Core save-boundary dispatch is `efcore:event-dispatch`.

## Agreed

_Nothing yet further._ Propose a rule through `dotnet:learning`'s convention procedure.
