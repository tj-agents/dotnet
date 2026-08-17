---
name: typescript-style
description: Generic TypeScript style for a hand-written client — `interface` for object shapes and `type` for unions, aliases and derived types, `extends` rather than intersections, camelCase fields matching the JSON wire key-for-key with no client-side case conversion (and the multipart form-field exception), defaulting absent values to `?: T` rather than `| null` unless "deliberately emptied" is a distinct acted-on state, and modelling server polymorphism as a discriminated union on the wire discriminator with a `never` exhaustiveness arm. Use when declaring or reviewing a type, adding a field that may be absent, seeing a non-camelCase key on the wire, or modelling a payload that arrives in more than one shape.
---

# typescript-style

This is a Claude Code compatibility stub. Do not edit skill instructions here.

Read and follow the canonical agent-agnostic skill at ../../../.agents/skills/typescript-style/SKILL.md.
