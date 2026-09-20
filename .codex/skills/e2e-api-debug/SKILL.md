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

Read and follow the [canonical shared definition](../../../.agents/operation/e2e-api-debug/SKILL.md) in full.
This discovery entry is generated; edit the referenced `.agents/` definition.
