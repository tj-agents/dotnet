---
name: scaffold
description: Create a new .NET project in the File structure `dotnet:structure-single-service` records. Use when starting a .NET project; it creates nothing until that File structure is agreed.
kind: utility
domain: dotnet
profile: scaffold
applicability: new .NET projects
requires: dotnet
provenance: house
---

# .NET project scaffold

Creates a .NET 10 `single-service` solution in the File structure `dotnet:structure-single-service` records.

## Create a project

```text
python -B <skill-directory>/scripts/scaffold.py new --name MyService --destination ~/source/repos --preset web --plugin-selection-adopter <machine-plugin-selection-skill-directory>/scripts/adopt_plugins.py
```

## Build and adapt

Use `--preset minimal` for a Web host with no persistence or test project. Configuration layers are defaults,
the preset, `--config options.json`, then repeated `--set key=value`; `--dry-run` prints the resolved result
without writing. The destination must already exist and `<destination>/<name>` must be new.
Use `--preset dapper-sqlserver` for a Web host with Dapper and SQL Server. The name must be a C# namespace whose
root segment is not `Program`.
Use `--preset sandbox` for Web, Functions with Durable support, worker, EF Core/PostgreSQL, OpenTelemetry and
unit plus integration project wiring.

`new` uses Core `machine:plugin-selection` to select the .NET stack, adding Azure when `cloud=azure`.
Selected plugins follow their marketplace main branches. A failed adoption or preflight leaves the
destination absent.

```text
python -B <skill-directory>/scripts/scaffold.py options --preset web
```

`add` is pending until the new-project workflow is stable.

## Azure hosting (`cloud=azure`)

`--set cloud=azure` wires health checks at `/health/live` and `/health/ready`, an Entra-based Npgsql
connection for `database=postgres` (via `Azure.Identity`), `UseAzureMonitor`/`AddAzureMonitorTraceExporter`
when `telemetry=opentelemetry`, SDK container publish for the worker, and an EF migration bundle plus
`infra/migration.Dockerfile` when using EF. `cloud=azure` requires `database` to be `none` or `postgres`;
`sqlserver` is rejected until azure has an Azure SQL component. The derived `infra/app.json` name is the
solution name lowercased with non-alphanumerics dropped, truncated to 12 characters; override it with
`--set cloud-name=<name>`.

`--set azure.<option>=<value>` forwards `<option>=<value>` to azure's own `scaffold.py`, and only when
`cloud=azure`; a `--config` file may hold an `"azure": {...}` object forwarded the same way. Give azure's
script with `new --azure-scaffold <path>` or the `AZURE_SCAFFOLD` environment variable; without either, the
command prints the exact azure invocation instead of running it. On a TTY, with no `--no-input` and no
`--dry-run`, `new` prompts for every unset option (and, once `cloud=azure` and azure's path is known, for
azure's own unset options).

```text
python -B <skill-directory>/scripts/scaffold.py new --name Sandbox --destination ~/source/repos --preset sandbox --set cloud=azure --azure-scaffold ~/source/repos/tj-agents/azure/.agents/azure/utility/scaffold/scripts/scaffold.py --plugin-selection-adopter <machine-plugin-selection-skill-directory>/scripts/adopt_plugins.py
```

## Validation and publication

The Core adoption helper requires Python 3.11 or later.

If the selected hosts include Functions, restore its project before the solution:

```text
dotnet restore src/MyService.Functions/MyService.Functions.csproj
```

Then restore, build and test every generated solution:

```text
dotnet restore MyService.slnx
dotnet build MyService.slnx --configuration Release
dotnet test MyService.slnx --configuration Release
```
