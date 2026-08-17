---
name: client-state
description: Client state ownership — a store is a private implementation detail of the feature that owns it, consumed through a facade hook rather than exported from the barrel or imported by a component, with every transition in a named store action, derived values computed from explicit inputs rather than stored or read off a singleton, one deliberate imperative session object for non-React consumers (route guards, request headers, logout) instead of a family of getter/setter wrappers, and server data never mirrored into the store. Use when adding client state, exposing state to components, writing a derivation over stored state, needing state outside React, or reviewing a `getState()`/`setState()` call.
---

# client-state

This is a Claude Code compatibility stub. Do not edit skill instructions here.

Read and follow the canonical agent-agnostic skill at ../../../.agents/skills/client-state/SKILL.md.
