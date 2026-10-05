---
name: skill-routes
description: Generate a .NET consumer repository's `.agents/skill-routes.json` and the registry of which repo gets which route-table kind, so `skill_router.py` gates its writes and reviews behind the owning dotnet and engineering standards. Use when wiring a .NET repo into skill routing, registering a new consumer repo, or changing what a path routes to.
kind: utility
domain: dotnet
profile: skill-routes
applicability: .NET consumer repositories wired for skill routing
requires: dotnet
provenance: house
---

# .NET skill routes

Generates the route tables `skill_router.py` reads. The row convention — floors, architecture-keyed
rows, the row fields — is owned by `engineering:skill-routes`; this skill owns the .NET derivation.
Its generator sits beside this file.

## Generate

```
python scripts/gen_skill_routes.py --kind dotnet-service --into <repo>      # a consumer's committed table
python scripts/gen_skill_routes.py --kind dotnet-service --into <repo> --check
python scripts/gen_skill_routes.py --emit-registry <dir>                    # registry.json + one table per kind
python scripts/gen_skill_routes.py --emit-registry <dir> --check
```

The committed `--into` table is the mechanism the router resolves today; the emitted registry becomes
live only once a routes directory ships beside the installed router. Adding a consumer repo is one
`REGISTRY` row in the generator.

## Kinds

- `dotnet-service` — a carved or standalone .NET service, no frontend: the meta rows, the dotnet rows,
  the `.cs` floor anchored at the repo root.
- `dotnet-service-with-app` — **not yet.** The frontend seam is gated on `POLYREPO_ROADMAP §6/§4c`.
