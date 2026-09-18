---
name: domain-events
description: Domain events in a .NET service — a domain method raises an event on the entity instead of calling a bus, the entity composes an event-raiser collection rather than inheriting an aggregate base, a SaveChanges interceptor clears then dispatches in a pre-commit phase that joins the caller's transaction and a post-commit phase that does not, one pre-commit handler per event translating the domain event into the published integration event so the outbox row commits atomically with the state change, handlers registered against the closed IDomainEventHandler<TEvent> interface because a concrete-only registration dispatches to nothing silently, and the anti-patterns (publishing alongside the write, injecting a bus into the domain project, business logic in a handler, raising from a setter). Use when a state change must announce itself, adding or reviewing a domain event or its handler, deciding pre-commit versus post-commit, wiring an integration-event publish, or when a domain project is about to take an infrastructure dependency.

kind: contract
---

# domain-events

The standard is `standards/dotnet/structure/DOMAIN_EVENTS.md` in `tomjseery/dotagents`, deployed to `~/.agents/standards/dotagents/dotnet/structure/DOMAIN_EVENTS.md`. Read it and follow it; this skill only routes to it.
