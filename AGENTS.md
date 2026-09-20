# dotagents

Read README.md and SOURCE_LAYOUT.md before changing repository structure.

Authored generic .NET capabilities live once under `.agents/<kind>/<name>/SKILL.md`. `.agents/plugins/sources.json`
owns the source map and generated-root declaration. `.agents/skills/`, `.codex/skills/`, `.claude/skills/`,
`.agents/INDEX.md`, both marketplace bridges, and `plugins/*` are generated. Authored host manifests live under
`.agents/plugins/manifests/`. Run `pwsh .agents/sync-generated.ps1` after authored changes and require
`pwsh .agents/sync-generated.ps1 -Check` before delivery.

Every definition declares its profile, applicability, prerequisites, and provenance. Core C# guidance must remain
usable without ASP.NET Core, EF Core, tenancy, gRPC, Aspire, microservices, or Tommy's selected library stack.
Optional profiles activate only when the consuming repository selects their prerequisite. Concrete product harness
commands and rosters stay with their product owner.
