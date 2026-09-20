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

## Applicability

This operation applies only when a repository exposes both a service E2E tier and a browser E2E tier over the
same stack. The consuming repository owns the concrete commands, topology, resources, and readiness gates.

## Procedure

1. Read both repository-owned entrypoints and confirm they must not boot concurrently.
2. Run the service tier first with `dotnet:e2e-api-debug`; it isolates backend and asynchronous behavior without browser noise.
3. Drive every service-tier failure to green before starting the browser tier.
4. Run the browser tier with `dotnet:e2e-ui-debug` and diagnose only failures that remain.
5. Report each tier's scenario counts and terminal result against the same source revision.

Use `engineering:failure-provenance` for pre-existing failures and `engineering:remote-validation` for the
exact-head remote checkpoint.
