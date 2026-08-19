---
name: keyed-strategies
description: The standard shape for behaviour that varies by a closed key in a .NET service — one module-local generic factory owning keyed DI resolution, operation-specific named facades that delegate through it, a registration builder that declares every family vertically and rejects duplicate keys, incomplete coverage and conflicting lifetimes so adding an enum member fails composition, and the anti-patterns it replaces (branching on the key inside key-agnostic code, service location outside the factory, parallel hand-written maps, returning an enum every caller re-switches on, throwaway result records, discard-tuple calls). Use when behaviour differs per enum/discriminator value, when adding a value to such an enum, when tempted to write a `switch` on a type/kind/mode key, or when reviewing keyed DI registrations.
---

# keyed-strategies

The standard is `standards/dotnet/structure/KEYED_STRATEGIES.md` in `tomjseery/dotagents`, deployed to `~/.agents/standards/dotagents/dotnet/structure/KEYED_STRATEGIES.md`. Read it and follow it; this skill only routes to it.
