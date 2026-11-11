---
name: libraries
description: Use when adding or replacing a .NET dependency; keep one library per job and apply only explicitly selected stack defaults.
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

## Example

```text
Existing library already does the job -> replace it, or do not add a second library.
```
