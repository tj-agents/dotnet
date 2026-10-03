---
name: debug-e2e-ui
description: Run and repair a repository's browser end-to-end tier through its own full-stack harness, checking readiness and server or RPC failures before browser console, UI and screenshot evidence, while preserving scenario semantics. Use when a browser E2E scenario or UI full-stack CI job fails.
kind: operation
domain: dotnet
profile: e2e
applicability: browser end-to-end suites using a repository-owned full-stack harness
requires: browser-e2e, playwright
provenance: operation, selected-stack
---

# Debugging a browser end-to-end suite

Read and follow the [canonical definition](../../../.agents/dotnet/operation/debug/e2e-ui/SKILL.md) in full.
This discovery entry is generated; edit the referenced `.agents/` definition.
