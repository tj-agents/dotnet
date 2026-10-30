---
name: authorization
description: Authorization standard for an ASP.NET Core service, whatever decides access (an in-process role table, OpenFGA, Cedar, OPA) — identity-only tokens with authority resolved per request, permission checks never role checks, a closed typed permission catalog, deny by default, ASP.NET Core policies and resource handlers as the only enforcement path, object-level checks beside every function-level one, one decision point with an AuthZEN-shaped contract, immediate revocation, an exhaustively tested model, a generated client catalog, escalation guards, separate operator authority and audited decisions. Use when adding a permission, role or protected endpoint, designing or reviewing an authorization model, or deciding where an access check runs.
kind: contract
domain: dotnet
profile: aspnet
applicability: ASP.NET Core services that authorize users
requires: aspnet-core
provenance: framework, house
---

# Authorization

Read and follow the [canonical definition](../../../.agents/dotnet/contract/authorization/SKILL.md) in full.
This discovery entry is generated; edit the referenced `.agents/` definition.
