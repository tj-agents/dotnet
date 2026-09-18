---
name: result-terminals
description: Turning a Result or Option into a response at the edge of a .NET service — the `Reunion.AspNetCore` terminals (`ToOkOrProblem`, `ToNoContentOrProblem`, `ToCreatedOrProblem`, `ToCreatedAtActionOrProblem`, `ToActionResult`, `ToResults`, `ToOkOr`, `ToOkOrNotFound`, `ToOkOrNoContent`), importing exactly one adapter namespace per file, automatic semantic-kind-to-status mapping for `IError`, projected overloads instead of a `Map` immediately before a terminal, normalizing only known dependency faults into 503/504, never normalizing cancellation, worker and RPC-server terminal policy, and the test matrix a Result-based change owes. Use when writing or reviewing a controller action, a minimal-API endpoint, a worker loop, or an RPC server method that returns a Result, or when deciding what an unexpected exception should become.

kind: contract
---

# result-terminals

The standard is `../../standards/dotnet/results/TERMINALS.md`, shipped in this plugin. Read it and follow it; this skill only routes to it.
