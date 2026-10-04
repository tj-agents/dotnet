---
name: microservice-boundaries
description: What one .NET service may depend on and how services talk — adapter services every host needs versus data services that must never depend on each other's runtime, cross-service coupling through published contracts and events only, and the protocol decision table (gRPC by default for internal synchronous hops; HTTP only at the forced boundaries of browser, third-party callers and OAuth; a message bus for fire-and-forget) plus typed Refit clients for third-party REST, why consuming your own service over HTTP means two contract surfaces, the ingress/load-balancing traps of serving gRPC and HTTP from one host, and what Aspire's `AddServiceDiscovery()`/`AddServiceDefaults()` do and pointedly do not do. Use when designing anything that crosses a service boundary, adding a startup dependency or health wait, choosing a protocol for a new hop, adding an outbound HTTP client, or reviewing a change that makes one service await another.
kind: contract
domain: dotnet
profile: distributed-services
applicability: distributed services
requires: distributed-service-architecture
provenance: architecture, selected-stack
---

# Service boundaries and communication

Read and follow the [canonical definition](../../../.agents/dotnet/contract/microservice/boundaries/SKILL.md) in full.
This discovery entry is generated; edit the referenced `.agents/` definition.
