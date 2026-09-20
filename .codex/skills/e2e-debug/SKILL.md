---
name: e2e-debug
description: Run a repository's service and browser end-to-end tiers in dependency order, driving the service tier green before the browser tier and reporting both against one source revision. Use only when both selected tiers need a complete sweep.
kind: operation
domain: dotnet
profile: e2e
applicability: repositories that provide both service and browser end-to-end tiers
requires: service-e2e, browser-e2e
provenance: operation, selected-stack
---

# Sweeping service and browser end-to-end tiers

Read and follow the [canonical shared definition](../../../.agents/operation/e2e-debug/SKILL.md) in full.
This discovery entry is generated; edit the referenced `.agents/` definition.
