---
name: libraries
description: Tommy's agreed .NET dependency policy — when to take a dependency and which are chosen. Read before writing or reviewing .NET that touches it; nothing applies until it is recorded here.
kind: contract
domain: dotnet
profile: core
applicability: .NET projects
requires: dotnet
provenance: house
---

# Dependency and library policy

Owns when to take a dependency and which ones are chosen.

**One library per job.** A second library for a job an existing one already does is the violation, even
when the newcomer is better in isolation. Replace, or don't add.

The concrete chosen libraries for Tommy's full selected .NET application stack are
`dotnet:libraries-selected`.

## Agreed

_Nothing yet further._ Propose a rule through `dotnet:learning`'s convention procedure.
