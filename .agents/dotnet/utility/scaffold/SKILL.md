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
python -B <skill-directory>/scripts/scaffold.py new --name MyService --destination ~/source/repos --preset api
```

## Build and adapt

Use `--preset minimal` for an API with no persistence or test project. Configuration layers are defaults,
the preset, `--config options.json`, then repeated `--set key=value`; `--dry-run` prints the resolved result
without writing. The destination must already exist and `<destination>/<name>` must be new.
Use `--preset dapper-sqlserver` for an API with Dapper and SQL Server. The name must be a C# namespace whose
root segment is not `Program`.
Use `--preset sandbox` for API, Functions with Durable support, worker, EF Core/PostgreSQL, OpenTelemetry and
unit plus integration project wiring.

```text
python -B <skill-directory>/scripts/scaffold.py options --preset api
```

`add` is pending until the new-project workflow is stable.

## Validation and publication

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
