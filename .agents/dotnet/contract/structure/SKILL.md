---
name: structure
description: Tommy's agreed .NET project structure — repository and module layout, visibility and wiring. Read before writing or reviewing .NET that touches it; nothing applies until it is recorded here.
kind: contract
domain: dotnet
profile: core
applicability: .NET projects
requires: dotnet
provenance: house
---

# Module structure

Owns the repository and module layout, visibility, and where dependencies are wired.

Layered module and shared-library structure is `dotnet:structure-modules` when a
project selects that architecture.

## Agreed

_Nothing yet further._ Propose a rule through `dotnet:learning`'s convention procedure.

## File structure

Project layout depends on the selected architecture. See `dotnet:structure-modules` for modular-service
and layered shared-library layout.

For `single-service`, the scaffold creates this layout; conditional entries are included only when the
corresponding option is selected:

```text
<Name>/
  <Name>.slnx
  .scaffold.json
  global.json
  Directory.Build.props
  Directory.Packages.props
  .editorconfig
  .gitattributes
  .gitignore
  AGENTS.md
  CLAUDE.md
  .github/workflows/ci.yml
  src/
    <Name>.Core/
      <Name>.Core.csproj
    <Name>.Infrastructure/                 when data is selected
      <Name>.Infrastructure.csproj
      ServiceCollectionExtensions.cs
      Persistence/ApplicationDbContext.cs  EF Core only
    <Name>.Api/                            when api is selected
      <Name>.Api.csproj
      Program.cs
      appsettings.json
    <Name>.Functions/                      when functions is selected
      <Name>.Functions.csproj
      Program.cs
      host.json
      local.settings.json
    <Name>.Worker/                         when worker is selected
      <Name>.Worker.csproj
      Program.cs
      appsettings.json
  BannedSymbols.txt                        when selected-stack is enabled
  tests/
    <Name>.UnitTests/                      when unit tests are selected
      <Name>.UnitTests.csproj
    <Name>.IntegrationTests/               when integration tests are selected
      <Name>.IntegrationTests.csproj
    <Name>.IntegrationTests.Fixtures/      when integration tests are selected
      <Name>.IntegrationTests.Fixtures.csproj
      ApiFixture.cs
```

`src` contains production projects and `tests` contains test projects. `Core` is infrastructure-free and
shared by hosts; it never references hosts or Infrastructure. Infrastructure references Core and supplies
selected persistence. Selected Api, Functions and Worker projects are process entry points and composition
roots; each references Core and Infrastructure when it is selected. Durable is an extension in Functions,
not a separate process or project. Integration fixture infrastructure belongs in its own project.

The paired instruction files describe the selected architecture and profiles. Root files pin tooling,
centralize package versions, configure formatting, provide CI and record scaffold provenance.

- The single-service tree keeps shared business logic infrastructure-free while allowing optional hosts and persistence; approved by Tommy on 2026-10-12 in the scripted-scaffold design.
