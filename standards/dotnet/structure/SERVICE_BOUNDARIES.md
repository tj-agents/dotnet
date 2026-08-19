# Service boundaries and communication

## Two kinds of service, two rules

- **Adapter services** — a shared runtime dependency present in every host (identity, payments). Any service
  MAY call one synchronously and MAY wait for it at startup, so those waits belong in the shared host helpers
  and apply everywhere.
- **Data services** — each owns its own data and audience. **A data service must never depend on another data
  service's runtime.** Cross-data-service coupling is published contracts and events only. A data service
  waiting on another data service at startup is the bug never to introduce: it re-creates the monolith's
  deployment coupling while keeping the cost of separate services.

Where a standalone host lacks another data service's events at seed time, the producing service ships a seeding
simulator that replays them — never run the other data service to fix it, and never write the projected rows
directly. See the `seeding` skill.

Shared code consumed by *every* service models the **intersection** of what its consumers need, never the
union. A member only ever populated or meaningful for one audience — dead weight for another — does not belong
on a shared type; either the caller resolves it and passes it in, or it lives in a separate abstraction only the
services with that concept depend on.

**Never share a transaction across services.** Coordinate with messages through an outbox.

## The protocol is chosen by the consumer, not by preference

If you can name who calls an endpoint, the protocol is already decided.

| Consumer | Protocol | Why |
|---|---|---|
| Your service → your service (sync) | **gRPC** | Both sides yours: contract-first `.proto`, HTTP/2 multiplexing, smaller payloads, codegen at both ends |
| Browser, mobile, or SPA | **HTTP/JSON** | A browser cannot open a raw gRPC connection — a hard limitation, not a choice |
| Third party calling in (webhooks) | **HTTP/JSON** | The third party dictates the protocol and always will |
| OIDC / OAuth token endpoints | **HTTP/JSON** | OAuth is HTTP by specification |
| Event-driven / fire-and-forget | **Message bus** | Already the seam; if the caller doesn't need an answer now, it is a message |

**The default is gRPC.** HTTP appears only at those forced boundaries, each one a case where something outside
your control dictates the wire format.

## Synchronous hops

- **One `.proto` per service is the single source of truth.** Codegen client and server from it — no
  hand-written contract on either side, no drift. Message and mapping conventions are in the `proto` skill.
- A service's RPC surface mirrors its in-process facade: the same command and query operations.
- Register clients with `AddGrpcClient<T>()` against a **logical service name** resolved by Aspire's
  `AddServiceDiscovery()`, never a hard-coded URL.
- Service-to-service auth is a `client_credentials` bearer token on the call metadata, from the same token
  service the rest of the platform uses.
- **Do not use gRPC-Web to reach a service from a browser.** Frontends go through that service's HTTP edge.

## HTTP surfaces

- **New endpoints** — minimal APIs. Webhooks and any net-new edge endpoint.
- **Existing public APIs** — controllers stay. Do not rewrite working edge endpoints for protocol consistency;
  the two converge over time, not urgently.
- **Consuming HTTP you don't own** — a typed **Refit** interface: a `[Get]`/`[Post]`-annotated contract
  registered with `AddRefitClient<T>()`, base address and any auth handler attached at registration. Do not
  hand-roll `IHttpClientFactory.CreateClient()` plus manual `JsonDocument` parsing for a call a typed interface
  expresses. Reach for raw `HttpClient` only where Refit genuinely cannot model the call.
- **Consuming your own HTTP internally — don't.** If both ends are yours the call is gRPC; Refit there means
  maintaining two contract surfaces for one service. The only acceptable case is a transition window before a
  service has its RPC surface, and it is temporary by definition.

A stateful **singleton** that injects a typed client captures one `HttpMessageHandler` for the process lifetime,
with no factory handler rotation. Accept that only for a stable, infrequently-hit internal endpoint, and never
copy the shape onto a hot or DNS-volatile client — those stay scoped or transient so the factory rotates
handlers normally.

## Serving gRPC and HTTP from one host

Some services need both — RPC for internal sync calls plus an HTTP webhook endpoint. Kestrel maps both in one
app; the traps are operational:

- **HTTP/2 end-to-end.** gRPC requires it. Over TLS it negotiates via ALPN, but the production ingress must
  speak HTTP/2 all the way through or the calls never reach the service.
- **Load balancing.** gRPC multiplexes over one long-lived connection, so a naive L4 balancer pins all traffic
  to one backend. Real per-call balancing needs a gRPC-aware L7 proxy.
- **Two cross-cutting surfaces.** Auth, error mapping, and logging are configured once *per protocol*;
  `AddServiceDefaults()` covers most of it for both.

## What Aspire does and does not give you

Aspire removes the *plumbing*, not the protocol decision:

- **`AddServiceDiscovery()`** — logical names resolve from injected configuration, so both `HttpClient` and
  gRPC channels target `http://payments` rather than an environment-specific URL.
- **`AddServiceDefaults()`** — one call applies OpenTelemetry, health checks, *and*
  `AddStandardResilienceHandler()` uniformly to gRPC and HTTP clients alike. That is the point of it: three
  cross-cutting concerns from one registration, not three separate opt-ins per client.
- **Typed clients** — `AddRefitClient<T>()` and `AddGrpcClient<T>()` both point at the logical service name;
  Aspire wires the rest.

Aspire does **not** generate `.proto`, share contracts, version anything, or handle auth — those stay yours.
That negative is here because it is the assumption people make.
