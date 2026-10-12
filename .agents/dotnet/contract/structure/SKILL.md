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

Repository and service layout follows the selected architecture.

## File structure

`dotnet:structure-single-service` owns the single-service repository layout. `dotnet:structure-modules` owns
modular-service and layered shared-library layout. Each architecture-specific contract applies only when its
architecture is selected.
