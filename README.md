# dotnet

Generic .NET guidance for Claude Code and Codex, published as `dotnet@dotagents`.
The canonical repository is [`tj-agents/dotnet`](https://github.com/tj-agents/dotnet); the marketplace ID remains `dotagents`.

## Skills

- Knowledge: `dotnet:direction`, `dotnet:knowledge`, `dotnet:learning`.
- Contracts: `dotnet:naming` (`naming:collaborators`, `naming:data-contracts`, `naming:mapping`, `naming:repositories`),
  `dotnet:style` (`style:comments`), `dotnet:structure` (`structure:modules`), `dotnet:domain-design`
  (`domain:ddd`, `domain:values`, `domain:events`), `dotnet:errors` (`errors:results`, `errors:carriers`,
  `errors:terminals`), `dotnet:testing` (`testing:unit`, `testing:integration`, `testing:e2e`), `dotnet:build`,
  `dotnet:libraries` (`libraries:selected`), `dotnet:keyed-strategies`, `dotnet:keyed-unions`, and the extras
  `dotnet:dependency-injection`, `dotnet:http-api`, `dotnet:logging`, `dotnet:microservice-boundaries`,
  `dotnet:multitenancy`, `dotnet:persistence`, `dotnet:proto`, `dotnet:seeding`, `dotnet:validation`.
- Operations: `dotnet:debug-integration`, `dotnet:debug-e2e`, `dotnet:debug-e2e-api`, `dotnet:debug-e2e-ui`.
- Utilities: `dotnet:scaffold`.

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
