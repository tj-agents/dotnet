---
name: e2e-ui-debug
description: Run the browser end-to-end suite (Reqnroll scenarios over Playwright against the full Aspire stack) and drive every failure to green — discover failures, re-run each one alone for the enriched output, and diagnose HTTP 4xx/5xx first, then a gRPC error in the callee's forwarded resource log, then browser console and on-screen errors, then the failure screenshot. Covers the entrypoint's command grammar and how to discover this repo's suites from it, headless as the default and why a direct dotnet test run is headed unless told otherwise, the startup-hang watch and the four causes that recur, preserving scenario semantics when changing a shared fixture or page object, and why widening a timeout or suppressing a build is banned rather than discouraged. Use whenever the user wants a browser E2E failure debugged, the full suite run, newly-passing or newly-failing scenarios discovered, or a flaky scenario investigated.

kind: contract
---

# e2e-ui-debug

The standard is `standards/dotnet/testing/E2E_UI_DEBUG.md` in `tomjseery/dotagents`, deployed to `~/.agents/standards/dotagents/dotnet/testing/E2E_UI_DEBUG.md`. Read it and follow it; this skill only routes to it.
