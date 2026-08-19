# Stack defaults

**One library per job.** A second library for a job an existing one already does is the violation, even
when the newcomer is better in isolation — two answers to one question is what makes a solution
unlearnable, and the migration that was supposed to follow never finishes. Replace, or don't add.

Each row has a skill covering *how* to use it well; this file only decides *what* and *when*.

| Job | Reach for | Depth |
|---|---|---|
| Relational data access | **EF Core** | `persistence` |
| A query EF expresses badly | **Dapper**, inside the repository | `persistence` |
| Results and errors | **Reunion** | `result-carriers` |
| Closed unions in domain and error code | **Dunet** source generator | `result-errors` |
| Single-value primitives worth a type | **Vogen** | — |
| Input shape validation | **FluentValidation** | `validation` |
| Logging | **`Microsoft.Extensions.Logging`** with `[LoggerMessage]` | `logging` |
| Telemetry | **OpenTelemetry** | — |
| Tests | **xUnit** | `unit-testing` |
| Mocking, at a genuine boundary only | **Moq** | `unit-testing` |
| Integration database | **Testcontainers** + **Respawn** | `integration-testing` |
| Browser end-to-end | **Reqnroll** + **Playwright** | `e2e-scenarios` |
| Architecture guards | **ArchUnitNET** | `unit-testing` |
| Internal synchronous calls | **gRPC** | `microservice-boundaries` |
| Third-party REST | **Refit** | `microservice-boundaries` |
| Outbound HTTP resilience | **`Microsoft.Extensions.Http.Resilience`** | — |
| Asynchronous messaging | a broker behind the solution's own abstraction | `microservice-boundaries` |
| Local orchestration | **.NET Aspire** | `microservice-boundaries` |
| API description | **Swashbuckle** | `http-api` |
| Package versioning | **MinVer**, from the tag | — |
| Analyzers | **Meziantou.Analyzer** + **BannedApiAnalyzers** | `csharp-style` |

## Prefer the platform to a package

`Microsoft.Extensions.*` and the BCL have absorbed most of what a library used to be needed for, and each
package not taken is one fewer thing to keep current across every service.

- **`TimeProvider`** for the clock, never `DateTime.Now` and never a hand-rolled `IClock`. It is testable
  out of the box with `Microsoft.Extensions.TimeProvider.Testing`.
- **`System.Text.Json`** for serialization. It is the framework's serializer, it is what ASP.NET Core
  already uses, and a second serializer in one process means two sets of naming and null rules.
- **`IHttpClientFactory`** for outbound HTTP lifetime, never a `new HttpClient()` held in a field.
- **`IOptions<T>`** bound from configuration, never configuration read by key at a call site.

## The analyzers are part of the stack, not a lint preference

A rule a machine can enforce is not a rule that belongs in prose. Meziantou's ruleset and
`BannedApiAnalyzers` carry the ones that can be, at **error** severity, so a violation cannot be merged
and argued about later.

**When a standard here is expressible as an analyzer rule, move it there and cut the prose to one line
plus the diagnostic id.** A banned API earns an entry in `BannedSymbols.txt` with the message naming what
to use instead — the message is read at exactly the moment someone reaches for the wrong thing, which is
the one place documentation always arrives on time.

## Deliberately not used

- **MediatR** — an in-process indirection layer over calls that already have interfaces. It hides the call
  graph, and its pipeline is a worse version of DI decorators.
- **AutoMapper** — mapping is `XMappers` extension methods: compile-checked, greppable, and debuggable.
  A convention-based mapper turns a renamed property into a runtime null rather than a build error.
- **Serilog, NLog** — `[LoggerMessage]` source generation is allocation-free and enforceable by analyzer.
- **Newtonsoft.Json** — superseded; a transitive reference from a shipped library is worse than a direct
  one, because every consumer inherits it.
- **A second Result library.** One carrier for the whole solution or none of the benefit: two means every
  boundary between them is a conversion, and both leak into the same signatures.
- **A second mocking or assertion library.** One per tier, chosen once — a solution with two teaches
  neither.
- **Whatever the solution has put in `BannedSymbols.txt`** — a banned API is a stack decision enforced at
  build time rather than a convention argued at review time.

If one of these looks necessary, the interesting question is why the incumbent cannot do the job. Answer
that in the PR, not in the `.csproj`.
