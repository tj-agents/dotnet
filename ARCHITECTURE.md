# Architecture

`tj-agents/dotnet` owns one scope: generic .NET guidance. It publishes one plugin, `dotnet`, while keeping optional application
profiles independently selectable inside that package.

## Authored

- `.agents/<kind>/<name>/SKILL.md` — full host-neutral capability definitions.
- `.agents/plugins/sources.json` — source map and exact generated roots.
- `.agents/plugins/payloads.json` — public package and selection profiles.
- `.agents/plugins/manifests/{codex,claude}/` — host-native manifest inputs.

## Generated

- `.codex/skills`, `.claude/skills` — host-specific thin discovery entries referencing canonical definitions.
- `.agents/INDEX.md` — kind/profile navigation.
- `.agents/plugins/marketplace.json`, `.claude-plugin/marketplace.json` — host marketplace bridges.
- `plugins/dotnet` — self-contained manifests, full definitions, index, and selection metadata.

Core C# rules have no stack prerequisite. Every other capability names the framework, library, architecture, or test
tier that makes it applicable. Generic debug operations discover a consuming repository's supported entrypoint;
product topology, commands, fixtures, and rosters remain with that product.
