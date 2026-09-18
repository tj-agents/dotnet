---
name: e2e-api-debug
description: Run the service end-to-end suite (xUnit over a full Aspire DistributedApplication with no browser, real payment test mode and a real Service Bus emulator) and drive every failure to green. Covers the three failure shapes and how to tell them apart — a synchronous status mismatch that already carries URL, status and response body; a polling timeout, which is the common one and means a downstream reaction never completed; and a completed flow that computed the wrong value — plus mapping the state that never appeared to the resource that owed it, why a gRPC error surfaces only in the callee's log, the startup-hang watch, and why widening a polling window is banned in a tier that has no baseline and no quarantine lane. Use whenever the user wants a service-layer E2E failure debugged, that suite run, or a settlement, payment or event-propagation flow investigated below the browser.

kind: contract
---

# e2e-api-debug

The standard is `../../standards/dotnet/testing/E2E_API_DEBUG.md`, shipped in this plugin. Read it and follow it; this skill only routes to it.
