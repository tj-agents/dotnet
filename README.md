# dotnet

Generic .NET guidance for Claude Code and Codex, published as `dotnet@dotagents`.
The canonical repository is [`tj-agents/dotnet`](https://github.com/tj-agents/dotnet); the marketplace ID remains `dotagents`.

## Skills

Families are folders, family first; a skill's name is its folder path joined by hyphens.

- Knowledge: `dotnet:learning`, `dotnet:knowledge`, `dotnet:direction`.
- Naming: `dotnet:naming`, `dotnet:naming-collaborators`, `dotnet:naming-repositories`,
  `dotnet:naming-dtos`, `dotnet:naming-mapping`.
- Style: `dotnet:style`, `dotnet:style-comments`.
- Structure: `dotnet:structure`, `dotnet:structure-modules`.
- Domain: `dotnet:domain-design`, `dotnet:domain-ddd`, `dotnet:domain-values`, `dotnet:domain-events`.
- Errors: `dotnet:errors`, `dotnet:errors-results`, `dotnet:errors-carriers`, `dotnet:errors-terminals`.
- Testing: `dotnet:testing`, `dotnet:testing-unit`, `dotnet:testing-integration`, `dotnet:testing-e2e`.
- Libraries: `dotnet:libraries`, `dotnet:libraries-selected`.
- Keyed: `dotnet:keyed-strategies`, `dotnet:keyed-unions`.
- Other contracts: `dotnet:build`, `dotnet:dependency-injection`, `dotnet:http-api`, `dotnet:logging`,
  `dotnet:microservice-boundaries`, `dotnet:multitenancy`, `dotnet:persistence`, `dotnet:proto`,
  `dotnet:seeding`, `dotnet:validation`.
- Operations: `dotnet:debug-integration`, `dotnet:debug-e2e`, `dotnet:debug-e2e-api`, `dotnet:debug-e2e-ui`.
- Utilities: `dotnet:scaffold`.

Renamed skills keep their old names as forwarding aliases; see [MIGRATION.md](MIGRATION.md).

## Applicability

The `core` profile holds only the family hubs and the naming/style family: no application-stack
prerequisite. Each required hub's family members — DDD, value semantics, domain events, EF Core
persistence, Reunion results and errors, ASP.NET Core, multitenancy, distributed services, every testing
tier, and Tommy's selected full application stack — are independent profiles with their own prerequisite.
Installing the plugin makes them all discoverable; a repository selects only the capabilities matching
its actual stack.

Concertable-specific rules and concrete harness commands remain in `Concertable/agents`. Machine and engineering
workflow capabilities remain in `tj-agents/core`. React and TypeScript guidance remains in
`tj-agents/react`.

## Authoring and verification

```powershell
pwsh .agents/sync-generated.ps1
pwsh .agents/sync-generated.ps1 -Check
python -B -m unittest discover -s .agents/tests -p "test_*.py"
```

The layout, the vendored generator and CI come from [kit](https://github.com/tj-agents/kit).
