---
name: structure
description: Tommy's agreed .NET project structure — repository and module layout, visibility and wiring. Read before writing or reviewing .NET that touches it; nothing applies until it is recorded here.
kind: contract
domain: dotnet
profile: core
applicability: .NET projects
requires: dotnet
provenance: house
---

# Module structure

Owns the repository and module layout, visibility, and where dependencies are wired.

Layered module and shared-library structure is `dotnet:structure-modules` when a
project selects that architecture.

## Agreed

_Nothing yet further._ Propose a rule through `dotnet:learning`'s convention procedure.

## File structure

Project layout depends on the selected architecture: see `dotnet:structure-modules`
for modular-service and layered shared-library layout. Once agreed for other architectures, this is
the tree `dotnet:scaffold` creates.
