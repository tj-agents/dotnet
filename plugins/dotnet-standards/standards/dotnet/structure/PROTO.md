# gRPC and Protobuf standard

Applies only to a service that actually owns or consumes a `.proto`. Protocol *selection* — whether a
hop is gRPC at all — is a separate decision and is not this skill's concern.

## Proto names are wire vocabulary, not your C# type names

A `.proto` message keeps the native RPC `*Response` / `*Request` naming. That name is generated,
wire-only, and never surfaces as the application payload type.

The C# payload is named for its shape, with no `Response` suffix — the `csharp-naming` skill owns that
rule and the alias escape hatch for an SDK collision.

```csharp
// CORRECT — proto keeps RPC vocabulary; the C# payload is named for what it is
Task<Result<Shipment, DispatchError>> DispatchAsync(...);

// WRONG — wire naming leaking into the application signature
Task<Result<ShipmentResponse, DispatchError>> DispatchAsync(...);
```

## Each side owns its own mappers

Proto ⇄ domain conversion follows the ordinary `XMappers` extension-class rule in `csharp-naming`, with
the client and server sides each owning their own mappers rather than sharing one.

```csharp
internal static class ShipmentMappers
{
    extension(Proto.ShipmentResponse response)
    {
        public Shipment ToShipment() => ...;
    }

    extension(Proto.ShipmentStatusType status)
    {
        public ShipmentStatus ToShipmentStatus() => ...;
    }
}
```

## What may cross the wire

The wire carries an **open string code, a published message, and a semantic kind**. It never carries a
discriminated-union type or a Result — those are in-process constructs.

A client maps an application-error `RpcException` back to its own operation-owned error with a **total**
`ToXError()` extension. Keep a private `FrozenDictionary<string, XError>` of reconstructible case
instances, keyed by code:

```csharp
private static readonly FrozenDictionary<string, OrderError> errors =
    new OrderError[]
    {
        new OrderError.CustomerNotFound(),
        new OrderError.AddressRejected()
    }
    .ToFrozenDictionary(error => error.Definition.Code);
```

Validate code, message, and kind. An unknown code — or a known code whose message or kind has changed —
throws an operation-specific **contract-mismatch** exception carrying the original `RpcException`. It
never degrades into a domain `Unknown` case, because that hides a deployment skew as a business outcome.

## Only reconstructible cases belong in the map

A payload-bearing case needs structured wire detail plus an explicit mapper that rebuilds the payload.
If the transport does not carry that data, **the case stays in-process** — never discard a payload to
force a case through code-only lookup.

## A gRPC client carries its credentials in `AddCallCredentials`, not at the call site

Register each generated client with `AddGrpcClient<T>` and attach the token in an `AddCallCredentials`
callback. The callback runs **per call** and resolves from the container at that moment, so a token that
expires mid-process is refreshed by the token service rather than frozen into the channel:

```csharp
services.AddGrpcClient<Proto.Escrow.EscrowClient>(o => o.Address = new Uri(address))
    .AddCallCredentials(async (_, metadata, sp) =>
    {
        var token = await sp.GetRequiredService<ITokenService>().GetTokenAsync("payments:write");
        metadata.Add("Authorization", $"Bearer {token}");
    });
```

The scope string belongs to the *client registration*, because it is a property of what that stub is
allowed to do — not of the individual call.

**The anti-patterns:** building the `Metadata` in the calling code and passing it to every stub method,
which puts an auth concern in every call site and lets one forget; and capturing a token when the client
is registered, which pins the process to the first token it ever got. When several stubs point at the same
service with the same scope, factor the callback into one extension rather than pasting the lambda per
client — a scope typo in one copy is a runtime 403 in one code path only.

## Cancellation takes precedence over error mapping

Catch caller cancellation *before* application errors and rethrow `OperationCanceledException` with the
caller's token. Unrelated availability, network, and protocol failures stay as their original
`RpcException` so retry and dead-letter behaviour still work.

Put the reusable cancellation predicate and operation-detail extraction in a shared gRPC utility
library; the concrete case map and the mismatch exception stay in the owning client.

## Enforcement

- Duplicate codes must fail a mapper contract test.
- Do not expose a public `TryToXError`, nullable parsers, parser-precedence chains, or runtime assembly
  discovery — the total mapper is the only entry point.
- Publish and deploy updated contracts and clients **before** a server emits a new code.
