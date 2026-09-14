---
name: e2e-debug
description: Run and fix both end-to-end tiers in one pass — the service tier (xUnit over the full Aspire stack, no browser) first, then the browser tier (Reqnroll over Playwright) — because the browser tier exercises the same services plus a browser, so a backend event flow that is red fails both and costs a browser timeout to diagnose instead of a resource log. Covers the shared pre-flight, why the two E2E applications must never boot concurrently, what each tier's failures look like once the other is green, and the per-tier verdict. Use when the user wants a complete E2E sweep, asks whether the E2E tests are green, or wants to know whether a browser failure is really a backend one — and prefer e2e-api-debug or e2e-ui-debug for a single tier.
---

# e2e-debug

The standard is `standards/dotnet/testing/E2E_DEBUG.md` in `tomjseery/dotagents`, deployed to `~/.agents/standards/dotagents/dotnet/testing/E2E_DEBUG.md`. Read it and follow it; this skill only routes to it.
