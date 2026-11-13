---
name: debug-e2e
description: Use when both .NET service and browser E2E tiers must be repaired; run the backend tier first and compare both at one revision.
kind: operation
domain: dotnet
profile: e2e
applicability: repositories that provide both service and browser end-to-end tiers
requires: service-e2e, browser-e2e
provenance: operation, selected-stack
---

# Sweeping service and browser end-to-end tiers

Read and follow the [canonical definition](../../../.agents/dotnet/operation/debug/e2e/SKILL.md) in full.
This discovery entry is generated; edit the referenced `.agents/` definition.
