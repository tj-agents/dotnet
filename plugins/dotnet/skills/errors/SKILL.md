---
name: errors
description: Tommy's agreed .NET error handling — error types, propagation and failure policy. Read before writing or reviewing .NET that touches it; nothing applies until it is recorded here.
kind: contract
domain: dotnet
profile: core
applicability: .NET projects
requires: dotnet
provenance: house
---

# .NET errors

Owns error types, how errors propagate, and what may fail fast.

Typed operation-owned error unions, when Reunion and Dunet are selected, are
`dotnet:errors-results`; converting Result/Option carriers is
`dotnet:errors-carriers`; turning a Result into a boundary response is
`dotnet:errors-terminals`.

## Agreed

_Nothing yet further._ Propose a rule through `dotnet:learning`'s convention procedure.
