---
name: typescript-style
description: Generic TypeScript style for a hand-written client — `interface` for object shapes and `type` for unions, aliases and derived types, `extends` rather than intersections, camelCase fields matching the JSON wire key-for-key with no client-side case conversion (and the multipart form-field exception), defaulting an absent value to an optional field rather than a nullable one unless "deliberately emptied" is a distinct acted-on state, and modelling server polymorphism as a discriminated union on the wire discriminator with a `never` exhaustiveness arm. Use when declaring or reviewing a type, adding a field that may be absent, seeing a non-camelCase key on the wire, or modelling a payload that arrives in more than one shape.
---

# typescript-style

The standard is `../../standards/react/TYPESCRIPT.md` in `tomjseery/dotagents`, deployed to `~/.agents/standards/react/TYPESCRIPT.md`. Read it and follow it; this skill only routes to it.
