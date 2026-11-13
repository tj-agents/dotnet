---
name: http-api
description: HTTP contract standard for a .NET service — services return application DTOs and never HTTP-flavoured `Response` types, controllers return the DTO verbatim unless the wire shape genuinely differs, write inputs are `Request` records in `XRequest.cs` files with identity from the route, no ASP.NET Core type in a service signature, action and route-segment naming, the idempotency hash, opt-in rate-limit policies, and translating a domain term into product vocabulary once at the Api layer. Use when adding or changing an endpoint, deciding whether a DTO needs a Response wrapper, shaping a write payload, naming a route or action, or throttling an endpoint.
kind: contract
domain: dotnet
profile: aspnet
applicability: ASP.NET Core HTTP APIs
requires: aspnet-core
provenance: framework, house
---

# HTTP API contracts

Read and follow the [canonical definition](../../../.agents/dotnet/contract/http-api/SKILL.md) in full.
This discovery entry is generated; edit the referenced `.agents/` definition.
