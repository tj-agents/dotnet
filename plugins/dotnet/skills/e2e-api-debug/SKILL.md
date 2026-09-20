---
name: e2e-api-debug
description: Run and repair a repository's service-level end-to-end tier through its own full-stack harness, separating response mismatches, polling timeouts and wrong completed values, tracing missing state to the responsible resource, and verifying the exact scenario plus its owning scope. Use when a service E2E scenario or backend full-stack CI job fails.
kind: operation
domain: dotnet
profile: e2e
applicability: service end-to-end suites using a repository-owned full-stack harness
requires: full-stack-test-harness
provenance: operation, selected-stack
---

# Debugging a service end-to-end suite

## Applicability

This operation applies only when the repository defines a service-level end-to-end tier over its full deployed
stack. The repository owns its orchestrator, external test modes, resource names, filters, and startup contract.

## Procedure

1. Read the repository's E2E entrypoint and list available suites or scopes before running anything.
2. Run the narrowest requested service scenario and monitor startup through the harness's supported logs.
3. Separate synchronous response mismatches, polling timeouts, and completed flows with an incorrect value.
4. For a timeout, map the missing state to the resource that owed it and inspect that resource's logs and dependencies.
5. Follow RPC faults to the callee and asynchronous faults through the producer, transport, and consumer chain.
6. Fix the cause; never widen a wait or suppress a scenario without measured evidence and an owned policy change.
7. Re-run the scenario, then the owning service E2E scope.

Use `engineering:failing-tests`, `engineering:failure-provenance`, and `engineering:remote-validation` for the
shared delivery rules. Use `dotnet:e2e-debug` only when both service and browser tiers must be swept.
