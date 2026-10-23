---
name: structure-single-service
description: The approved .NET single-service repository tree, optional hosts and persistence, and project reference direction. Read when selecting or scaffolding the single-service architecture.
kind: contract
domain: dotnet
profile: single-service
applicability: single-service architecture
requires: single-service-architecture
provenance: architecture, house
---

# Single-service structure

Owns the single-service repository layout, optional host projects and project reference direction.

## Applicability

This contract applies only to the single-service architecture and requires `single-service-architecture`.

## File structure

Project layout depends on the selected options; conditional entries are included only when the corresponding
option is selected:

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
    <Name>.Domain/
      <Name>.Domain.csproj
    <Name>.Application/
      <Name>.Application.csproj
    <Name>.Infrastructure/                 when data is selected
      <Name>.Infrastructure.csproj
      ServiceCollectionExtensions.cs
      Persistence/ApplicationDbContext.cs  EF Core only
    <Name>.Web/                            when web is selected
      <Name>.Web.csproj
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

`src` contains production projects and `tests` contains test projects. `Domain` holds entities, value objects
and domain events; it references nothing. `Application` holds services, repository interfaces, DTOs and
requests, and mappers; it references Domain. Its services follow `dotnet:structure-modules`' application
service role. Infrastructure references Application and Domain and supplies
selected persistence. Selected Web, Functions and Worker projects are process entry points and composition
roots; each references Application and Infrastructure when it is selected. Durable is an extension in
Functions, not a separate process or project. Integration fixture infrastructure belongs in its own project.

The paired instruction files describe the selected architecture and profiles. Root files pin tooling,
centralize package versions, configure formatting, provide CI and record scaffold provenance.

## Host naming

"Api" is a module's endpoint layer (`dotnet:structure-modules`' `X.Api`); "Web" is the process host that
serves the whole web API.

```text
<Name>.Web/              the process host — serves the whole web API
  <Name>.Web.csproj
<Module>.Api/             a module's endpoint layer (structure-modules)
  <Module>.Api.csproj
```
