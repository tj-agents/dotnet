---
name: http-api
description: HTTP contract standard for a .NET service — services return application DTOs and never HTTP-flavoured `Response` types, controllers return the DTO verbatim by default and a dedicated `Response` only where the wire shape genuinely differs or a public anonymous surface needs a frozen contract, write inputs are `Request` records with `{ get; init; }` and identity taken from the route rather than the body, a single shared request type until create and update contracts diverge, and translating a domain term into its product/API vocabulary exactly once at the Api layer. Use when adding or changing an endpoint, deciding whether a DTO needs a Response wrapper, shaping a write payload, or naming a route.
---

# http-api

This is a Claude Code compatibility stub. Do not edit skill instructions here.

Read and follow the canonical agent-agnostic skill at ../../../.agents/skills/http-api/SKILL.md.
