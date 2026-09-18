---
name: integration-debug
description: Run the in-process integration suite (xUnit over WebApplicationFactory, one real SQL container per fixture with Respawn between tests, every external mocked) and drive each failure to green. Covers discovering this repo's projects and scopes from the entrypoint's own listing rather than a remembered roster, reading the failure block in the one order that works — assertion message, then the per-test server-side log block, then the stack trace only if the test threw — the status-assertion message that already carries URL, status and response body, tracing a missing side-effect from its capturing mock back to a handler that was never invoked, seed data lost to reset ordering, and a foreign-key violation naming another module's table. Use whenever an integration test fails, a module's integration tests need rerunning, or a CI integration job needs narrowing to its smallest failing scope.

kind: contract
---

# integration-debug

The standard is `standards/dotnet/testing/INTEGRATION_DEBUG.md` in `tomjseery/dotagents`, deployed to `~/.agents/standards/dotagents/dotnet/testing/INTEGRATION_DEBUG.md`. Read it and follow it; this skill only routes to it.
