# dotnet

Generic .NET guidance for Claude Code and Codex, published as `dotnet@dotagents`.
The canonical repository is [`tj-agents/dotnet`](https://github.com/tj-agents/dotnet); the marketplace ID remains `dotagents`.

## Ownership

Full authored definitions live under `.agents/<kind>/<name>/SKILL.md`. The repository scope already means .NET,
so there is no repeated `dotnet/` source folder. `.codex/skills`, `.claude/skills`, marketplaces,
the capability index, and `plugins/dotnet` are generated from those definitions and authored host manifests.
See [SOURCE_LAYOUT.md](SOURCE_LAYOUT.md).

## Applicability

The `core` profile contains shared C# naming/style, comments, collaborator naming, data-contract naming,
mapping, and repository naming. Each has its own task trigger and no application-stack prerequisite.
EF Core persistence mechanics, HTTP and protobuf stay with their respective optional profiles.
ASP.NET Core, EF Core, multitenancy, distributed-service, modular-service, testing-tier, result-library, validation,
and full-stack defaults are independent profiles. Installing the plugin makes them discoverable; a repository selects
only the capabilities matching its actual stack.

Concertable-specific rules and concrete harness commands remain in `Concertable/agents`. Machine and engineering
workflow capabilities remain in `tj-agents/core`. React and TypeScript guidance remains in
`tj-agents/react`.

## Canonical naming and contract owners

Start with `csharp-naming` to select the relevant owner. A collaborator change includes its operation
and returned outcomes; its result profile is selected alongside its role. Source ownership is physical:
these definitions are separate authored skills with separate discovery triggers.

| Concern | Canonical source |
|---|---|
| Shared spelling, interface/type pairs and task routing | [csharp-naming](.agents/contract/csharp-naming/SKILL.md) |
| Collaborator responsibility, verb and semantic outcome | [collaborator-naming](.agents/contract/collaborator-naming/SKILL.md) |
| Meaning of DTOs, snapshots, summaries and projections | [data-contract-naming](.agents/contract/data-contract-naming/SKILL.md) |
| Pure conversion and receiver extensions | [mapping](.agents/contract/mapping/SKILL.md) |
| Repository capability, query names and storage returns | [repository-naming](.agents/contract/repository-naming/SKILL.md) |
| EF Core context/base bindings and persistence mechanics | [persistence](.agents/contract/persistence/SKILL.md) |
| In-process presence, failure and composition with Reunion | [result-carriers](.agents/contract/result-carriers/SKILL.md) |
| Input and domain validation contracts for the selected stack | [validation](.agents/contract/validation/SKILL.md) |
| HTTP and protobuf contracts | [http-api](.agents/contract/http-api/SKILL.md), [proto](.agents/contract/proto/SKILL.md) |
| DI registration and lifetime mechanics | [dependency-injection](.agents/contract/dependency-injection/SKILL.md) |

Core role conventions describe outcomes without requiring a result library. Selected profiles map
those outcomes to concrete types. An EF finder can return `T?`, an application resolver can return
Reunion `Option<T>`, and a domain validator can return Reunion `ValidationResult` within the same
project. Their role, operation, result and caller handling form one coherent contract. These are
canonical house conventions; framework/library-defined APIs retain their own names and signatures.

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
