# dotnet

Generic .NET guidance for Claude Code and Codex, published as `dotnet@dotagents` and the optional `efcore@dotagents`.
The canonical repository is [`tj-agents/dotnet`](https://github.com/tj-agents/dotnet); the marketplace ID remains `dotagents`.

## Skills

Families are folders, family first; a skill's name is its folder path joined by hyphens.

- Knowledge: `dotnet:learning`, `dotnet:knowledge`, `dotnet:direction`.
- Naming: `dotnet:naming`, `dotnet:naming-collaborators`, `dotnet:naming-dtos`.
- Style: `dotnet:style`, `dotnet:fields`, `dotnet:comments`.
- Structure: `dotnet:structure`, `dotnet:structure-modules`.
- Domain: `dotnet:domain-design`, `dotnet:domain-ddd`, `dotnet:domain-values`, `dotnet:domain-events`.
- Errors: `dotnet:errors`, `dotnet:errors-results`, `dotnet:errors-carriers`, `dotnet:errors-terminals`.
- Testing: `dotnet:testing`, `dotnet:testing-unit`, `dotnet:testing-integration`, `dotnet:testing-e2e`.
- Libraries: `dotnet:libraries`, `dotnet:libraries-selected`.
- Keyed: `dotnet:keyed-strategies`, `dotnet:keyed-unions`.
- Other contracts: `dotnet:build`, `dotnet:dependency-injection`, `dotnet:http-api`, `dotnet:logging`,
  `dotnet:mapping`, `dotnet:messaging`, `dotnet:microservice-boundaries`, `dotnet:proto`, `dotnet:repositories`, `dotnet:seeding`, `dotnet:validation`.
- EF Core: `efcore:persistence`, `efcore:multitenancy`, `efcore:specification`, `efcore:query-building`,
  `efcore:event-dispatch`. Install this plugin only for EF Core projects; it depends on `dotnet`.
- Operations: `dotnet:debug-integration`, `dotnet:debug-e2e`, `dotnet:debug-e2e-api`, `dotnet:debug-e2e-ui`.
- Utilities: `dotnet:scaffold`.

Renamed skills are listed in [MIGRATION.md](MIGRATION.md).

## Applicability

The `core` profile holds only the family hubs and the naming/style family: no application-stack
prerequisite. Each required hub's family members — DDD, value semantics, domain events, EF Core
persistence, Reunion results and errors, ASP.NET Core, multitenancy, distributed services, every testing
tier, and Tommy's selected full application stack — are independent profiles with their own prerequisite.
The `dotnet` plugin supplies generic guidance; `efcore` owns the EF Core-specific profiles. A repository
selects the plugins and capabilities matching its actual stack. Generic seeding and domain-event raising
remain in `dotnet`; their EF persistence and dispatch adapters live in `efcore`.

Concertable-specific rules and concrete harness commands remain in `Concertable/agents`. Machine and engineering
workflow capabilities remain in `tj-agents/core`. React and TypeScript guidance remains in
`tj-agents/react`.

## Authoring and verification

```powershell
pwsh .agents/sync-generated.ps1
pwsh .agents/sync-generated.ps1 -Check
python -B -m unittest discover -s .agents/tests -p "test_*.py"
```

The layout, the vendored generator and CI come from [Template](https://github.com/tj-agents/template).

Snippet source owners are explicit in the scaffold's manifest. In a checkout, the generator reads each
owner's authored contracts; in generated packages it reads the separate sibling payloads. Check that
layout with `python -B plugins/dotnet/.agents/dotnet/utility/scaffold/snippets/gen_snippets.py --check`.
If installed plugin payloads occupy unrelated cache directories, bind the owning source explicitly:
`--contract-root efcore=<efcore-plugin-root>/.agents/efcore/contract`. No EF source is copied into dotnet.
