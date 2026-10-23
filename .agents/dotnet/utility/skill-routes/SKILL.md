---
name: skill-routes
description: Generate a .NET consumer repository's `.agents/skill-routes.json` and the registry of which repo gets which route-table kind, so `skill_router.py` gates its writes and reviews behind the owning dotnet and engineering standards. Use when wiring a .NET repo into skill routing, registering a new consumer repo, or changing what a path routes to, or selecting ORM-independent versus EF Core routes.
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
python scripts/gen_skill_routes.py --kind dotnet-service --into <repo>      # the consumer's table
python scripts/gen_skill_routes.py --kind dotnet-service --into <repo> --check
python scripts/gen_skill_routes.py --kind efcore-service --into <ef-core-repo>
python scripts/gen_skill_routes.py --emit-registry <dir>                    # registry.json + one table per kind
python scripts/gen_skill_routes.py --emit-registry <dir> --check
python scripts/gen_skill_routes.py --emit-tiers <dotnet-repo>              # routes in .agents/tiers/*.json
python scripts/gen_skill_routes.py --emit-tiers <dotnet-repo> --check
```

The `routes` in the shipped `dotnet` and `efcore` tier declarations are what gate a repository with no
table of its own, so every repository the tier detects is gated without a per-repository step. Rerun
`--emit-tiers` after changing a row.

The `--into` table is the mechanism the router resolves today; the emitted registry becomes live only
once a routes directory ships beside the installed router. Adding a consumer repo is one `REGISTRY`
row in the generator.

## Kinds

- `dotnet-service` — a carved or standalone .NET service, no frontend: meta and generic .NET rows,
  with the `.cs` floor anchored at the repo root. It never requires an EF Core plugin.
- `efcore-service` — the same service with EF Core selected: adds the `efcore` layer and its persistence,
  specification, query-building, event-dispatch and tenancy rows. EF scaffolds choose this kind from
  their selected data option; Dapper-only and no-database scaffolds keep `dotnet-service`.
- `dotnet-service-with-app` — **not yet.** The frontend seam is gated on `POLYREPO_ROADMAP §6/§4c`.
