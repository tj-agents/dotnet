# dotnet

Generic .NET guidance for Claude Code and Codex, published as `dotnet@dotagents`.
The canonical repository is [`tj-agents/dotnet`](https://github.com/tj-agents/dotnet); the marketplace ID remains `dotagents`.

## Ownership

Full authored definitions live under `.agents/<kind>/<name>/SKILL.md`. The repository scope already means .NET,
so there is no repeated `dotnet/` source folder. `.codex/skills`, `.claude/skills`, marketplaces,
the capability index, and `plugins/dotnet` are generated from those definitions and authored host manifests.
See [SOURCE_LAYOUT.md](SOURCE_LAYOUT.md).

## Applicability

The `core` profile contains only comments, C# naming, and C# style and has no application-stack prerequisite.
ASP.NET Core, EF Core, multitenancy, distributed-service, modular-service, testing-tier, result-library, validation,
and full-stack defaults are independent profiles. Installing the plugin makes them discoverable; a repository selects
only the capabilities matching its actual stack.

Concertable-specific rules and concrete harness commands remain in `Concertable/agents`. Machine and engineering
workflow capabilities remain in `tj-agents/core`. React and TypeScript guidance remains in
`tj-agents/react`.

## Authoring and verification

Each definition declares `kind`, `domain`, `profile`, `applicability`, `requires`, and `provenance`. After an authored
change run:

```powershell
pwsh .agents/sync-generated.ps1
pwsh .agents/sync-generated.ps1 -Check
python -B -m unittest discover -s .agents/tests -p "test_*.py"
```

The generator rejects source-map drift, unsafe output roots, duplicate identities, unresolved local skill references,
missing selection metadata, product-owner leakage, and inconsistent host manifests.
