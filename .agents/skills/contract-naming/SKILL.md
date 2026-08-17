---
name: contract-naming
description: Naming the client's half of an HTTP contract — reads take the plain domain noun with no `Dto` or `Response` suffix (those are the server's words and differentiate nothing on the client), writes take `XRequest` carrying only client-settable fields with identity coming from the route, a suffix survives only where it distinguishes two real shapes, and every feature's reads and requests live in one `types.ts` the api module imports. Use when naming a type that mirrors a server payload, shaping a write body, deciding whether to keep a suffix, choosing where a contract type lives, or weighing generated clients against hand-written types.
---

# Contract naming

## Reads are named for the domain noun — no `Dto`, no `Response`

A type that mirrors a server **read** is named for the *thing*: `Order`, `Shipment`, `Checkout`,
`Invoice`. No suffix.

`Dto` and `Response` are the *server's* words. `Dto` is server-side layering that keeps services callable
off the HTTP layer; it never had meaning on the client. `Response` describes what the server *sends* from
the server's viewpoint — but to the client that payload is just an `Order`. Those suffixes are idiomatic
only in **machine-generated** clients, which mirror the server's schema names verbatim. A hand-written
client drops them.

**Litmus:** *rename this type — does any JSON byte change? No → the name is yours; name it for the domain.*

> **Anti-pattern:** a read type named with a server suffix — `PaymentResponse`, `TicketPurchaseResponse`. A
> payment *outcome* is a domain noun: `PaymentOutcome`. A ticket purchase is a `TicketPurchase`.

**The general rule: a suffix must distinguish two real shapes *here*.** The server needs
Entity/Dto/Response because it genuinely holds three shapes of one concept. The client holds *one* shape
per concept — the thing it receives — so `Response` differentiates nothing and is pure noise. Before
keeping any suffix, ask what the *unsuffixed* name would collide with. If the answer is "nothing", drop it.

That test is exactly what keeps the suffixes that do survive:

- **`XRequest`** — a real second shape, the write payload sitting beside the read.
- **A third-party envelope** — a raw provider response whose shape genuinely differs from the domain value
  handed back from it (`GeocodeResponse` → `Coordinates`).
- **`XPayload`** — event-carried data on a realtime handler, a different axis from read/write. It earns the
  suffix where the event shape differs from the HTTP read, or where it names an otherwise-anonymous
  primitive. A **pure alias** of an already-domain-named type does not: delete it and let handlers take the
  domain type.

## Write inputs are `XRequest`, carrying only client-settable fields

The body sent to a write endpoint — and passed as the mutation's variables — is `XRequest`:
`CreateOrderRequest`, `UpdateShipmentRequest`.

This is not a leaked server word, and that is precisely why it survives when `Response` did not:

- `Response` is the server's word for what the client *receives*. `Request` is **the client's own accurate
  word** — the client is literally constructing an HTTP request. It describes what the code is doing from
  *its* viewpoint.
- It mirrors the server's request records 1:1, so **one greppable name spans the whole stack**, and nothing
  needs renaming if the project ever adopts codegen, which would emit exactly this name.

A query library names only the *variables slot* in its generic, never a type suffix, so it imposes nothing
here. `Input` is a real alternative but is GraphQL-native — it exists there to dodge a namespace collision
REST does not have — and adopting it would add a gratuitous `Request`→`Input` translation over a server
that already says `Request`.

```ts
// CORRECT — the client's half of the contract; the server stamps user, time, and IP
export interface SignatureRequest {
  signatoryName: string;
  drawnSignatureImage?: string;
}
```

- **Route or resource identity is a function argument, never a body field** —
  `signContract(contractId, signature)`.
- **Share one `XRequest`** where create and update take the identical writable shape; split into
  `CreateXRequest`/`UpdateXRequest` the moment they diverge.
- Absence follows the `undefined` rule in the `typescript-style` skill.

**Litmus:** *could the client legitimately set this field on the way in? No — it's a route id, or
server-owned → it is not in the `Request`.*

> A genuine domain noun that happens to describe a pre-submit shape (`OrderDraft`) is not a stand-in for
> `Request`. Keep it.

## Contract types live in the feature's `types.ts`

Every feature owns one `features/<feature>/types.ts` holding its domain reads *and* its `XRequest` inputs.
The feature's `api/xApi.ts` **imports** them and never declares its own. Feature-folder colocation is the
standard structure, and one file answers "what does this feature exchange with the server".

Name the type — rather than inlining the object — once it crosses a function boundary: it is the declared
mutation-variables type, or it is shared by the api function and a hook or component. Inline anonymous
object types only for a genuinely single-use, one-or-two-field body at one call site.

**Litmus:** *to see everything this feature exchanges with the server, is one file enough?*

## Hand-written, by choice

Hand-writing these types is what lets the client name for its own domain and viewpoint. The cost is silent
drift from the server, which is acceptable only while the surface is small and co-owned.

If the project does adopt codegen, generate **types only**, into a quarantined module, and re-export
domain-named aliases from it. Never let generated `XResponse`/`XDto` names reach feature code.
