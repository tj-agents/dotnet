---
name: result-terminals
description: Turning a Result or Option into a response at the edge of a .NET service — the `Reunion.AspNetCore` terminals (`ToOkOrProblem`, `ToNoContentOrProblem`, `ToCreatedOrProblem`, `ToCreatedAtActionOrProblem`, `ToActionResult`, `ToResults`, `ToOkOr`, `ToOkOrNotFound`, `ToOkOrNoContent`), importing exactly one adapter namespace per file, automatic semantic-kind-to-status mapping for `IError`, projected overloads instead of a `Map` immediately before a terminal, normalizing only known dependency faults into 503/504, never normalizing cancellation, worker and RPC-server terminal policy, and the test matrix a Result-based change owes. Use when writing or reviewing a controller action, a minimal-API endpoint, a worker loop, or an RPC server method that returns a Result, or when deciding what an unexpected exception should become.
kind: contract
domain: dotnet
profile: results
applicability: ASP.NET Core or worker/RPC edges using Reunion carriers
requires: reunion, aspnet-core-or-worker-rpc
provenance: library, framework, house
---

# Result terminals

Read and follow the [canonical shared definition](../../../.agents/contract/result-terminals/SKILL.md) in full.
This discovery entry is generated; edit the referenced `.agents/` definition.
