---
name: debug-e2e-ui
description: Use when a .NET browser E2E scenario fails; check stack readiness, transport/server faults, console output and the real trace or screenshot.
kind: operation
domain: dotnet
profile: e2e
applicability: browser end-to-end suites using a repository-owned full-stack harness
requires: browser-e2e, playwright
provenance: operation, selected-stack
---

# Debugging a browser end-to-end suite

Owns reproducing and repairing a failing browser E2E scenario through its full-stack harness.

## Applicability

This operation applies only when the repository defines a browser E2E tier and supplies its own full-stack
entrypoint, scenario filters, resource logs, and artifact locations.

## Procedure

1. Discover the repository's supported browser suites and run the narrowest failing scenario headless.
2. Confirm the full stack reached its declared ready state before interpreting a browser timeout.
3. Diagnose HTTP 4xx/5xx first, then callee-side RPC/resource logs, then browser console and visible UI errors.
4. Inspect the failure screenshot or trace only after transport and server failures are ruled out.
5. Preserve the scenario's behavior when changing shared fixtures, page objects, or fast-forward setup.
6. Fix the cause; do not widen timeouts, suppress builds, or move a failing scenario into an ignore list.
7. Re-run the scenario alone, then its owning browser suite.

Use `engineering:failing-tests`, `engineering:failure-provenance`, and `engineering:remote-validation` for the
shared delivery rules. Use `dotnet:testing-e2e` for scenario authoring.

## Example

```text
Browser timeout -> confirm stack readiness -> inspect HTTP, RPC, and resource logs -> inspect the trace.
```
