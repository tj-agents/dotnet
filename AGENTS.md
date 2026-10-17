# dotnet

This repository uses the plugin layout `template:check` documents and enforces
(https://github.com/tj-agents/template). Authored skills live once under `.agents/<plugin>/<kind>/<name>/SKILL.md`,
with each skill's scripts and templates beside it; related skills share a family folder, family first
(`naming/collaborators/` publishes `naming-collaborators`). `.agents/sync_generated.py`, `.agents/sync-generated.ps1`,
`.gitattributes`, `.gitignore`, `CLAUDE.md` and `.github/workflows/ci.yml` are vendored from the current Template.
Change them in Template, then run `template:update` to refresh them.

`.codex/skills/`, `.claude/skills/`, `.agents/INDEX.md`, both marketplace files and `plugins/*` are generated. Run
`pwsh .agents/sync-generated.ps1` after authored changes and require `pwsh .agents/sync-generated.ps1 -Check`
before delivery.

`knowledge` is Tommy's progress record: change it only under `learning`'s Progress rules. A `contract`
skill gains a rule only through `learning`'s convention procedure, after Tommy decides it.

Core C# guidance must remain usable without ASP.NET Core, EF Core, tenancy, gRPC, Aspire, microservices, or
Tommy's selected library stack: the required hubs (`style`, `structure`, `domain-design`, `errors`, `testing`,
`build`, `libraries`, the `naming` family, `fields`, `comments`, `mapping`, `repositories`) stay stack-free in `core`, and every prerequisite-bearing
family member keeps its own profile one level down. Concrete product harness commands and rosters stay with
their product owner.
