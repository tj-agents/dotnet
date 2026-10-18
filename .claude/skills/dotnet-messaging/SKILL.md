---
name: messaging
description: Integration-event messaging roles — the one generic `IIntegrationEventPublisher` per solution, staging events in the caller's unit of work, and the `<Subscription>Processor` `BackgroundService` that pumps one broker subscription, dispatches each message to its `<Event>Handler` in a fresh scope and settles it. Use when publishing an integration event, consuming a broker subscription, or naming either role.
kind: contract
domain: dotnet
profile: distributed-services
applicability: services publishing or consuming integration events through a message broker
requires: message-broker
provenance: architecture, house
---

# Messaging

Read and follow the [canonical definition](../../../.agents/dotnet/contract/messaging/SKILL.md) in full.
This discovery entry is generated; edit the referenced `.agents/` definition.
