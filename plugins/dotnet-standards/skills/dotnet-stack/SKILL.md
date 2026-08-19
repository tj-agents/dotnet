---
name: dotnet-stack
description: Which .NET library to reach for which job and what is deliberately not used — EF Core with Dapper only inside the repository, Reunion for results, Dunet for closed unions, Vogen for single-value primitives, FluentValidation for input shape, LoggerMessage over Serilog, xUnit with Moq only at genuine boundaries, Testcontainers plus Respawn, Reqnroll plus Playwright, ArchUnitNET, gRPC internally and Refit for third-party REST, Aspire for local orchestration, MinVer for versioning, plus preferring the platform (TimeProvider, System.Text.Json, IHttpClientFactory, IOptions) over a package, treating analyzers and BannedSymbols as part of the stack rather than a lint preference, and the not-used list (MediatR, AutoMapper, Serilog, Newtonsoft.Json, a second Result or mocking or assertion library). Use when adding a package reference, choosing a library for a new job, wondering whether something is already solved in the BCL, or reviewing a PR that introduces a dependency overlapping one already in the solution.
---

# dotnet-stack

The standard is `../../standards/dotnet/STACK.md`, shipped in this plugin. Read it and follow it; this skill only routes to it.
