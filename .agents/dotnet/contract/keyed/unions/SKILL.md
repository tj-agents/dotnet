---
name: keyed-unions
description: The standard shape for behaviour that varies by a closed key when the variants do NOT share one signature — a union resolved by key whose arms differ in parameters or return type, the sibling of `keyed-strategies` (N implementations of one identical interface). Covers the deciding question (declare a second arm only for a genuine difference in parameters or return type; identical headers are one interface with two implementations), the key going in and a capability coming out so business code never names the key, the registration block as the readable capability partition with completeness validation, arms growing with capabilities rather than keys, each arm matched exactly once, preconditions belonging in validation rather than arm implementations, arms carrying real payloads (no empty cases, marker-interface arms, or nullable fields standing in for absence), never inventing a parameter object to force differently-shaped arms into one signature, shared data living outside the union because C# 15 unions have no shared state across cases, and Dunet as the interim mechanism including the per-union implicit-conversion decision. Use when behaviour varies by a closed key and the variants take different inputs, when adding a key to such a family, when deciding between a union arm and another implementation of an existing interface, when a match arm needs a `when` guard or a discard, or when reviewing a keyed union registration.
kind: contract
domain: dotnet
profile: keyed-design
applicability: closed-key variants with different signatures
requires: dunet
provenance: library, pattern, house
---

# Keyed unions

Owns the shape for behaviour that varies by a closed key when the variants have different signatures.

## Applicability

This contract applies only to closed-key variants with different signatures. It requires `dunet`. Installing `dotnet@dotagents` makes this guidance available; it does not select those technologies for a consuming repository.

**When behaviour varies by a closed key and the variants do not share one signature**, resolve a *union* by
key rather than a strategy. `dotnet:keyed-strategies` owns the other half; the two are different patterns sharing
a registration mechanism, and applying the strategy rules to a union problem is the failure this document
exists to prevent.

| | keyed strategy | keyed union |
|---|---|---|
| Shape | N implementations of **one identical interface** | N arms of **different shapes** |
| Caller | resolves and calls, never knowing which it got | matches and does something **different** per arm |
| Adding a key | register another implementation | usually register against an **existing** arm |

**Only declare a second arm when the arms genuinely differ in parameters or return type.** Two arms whose
method headers are identical are one interface with two implementations — that is the strategy half doing its
job *inside* an arm, not a reason to split the union. This is the single most useful review question.

## The key selects; the capability is returned

The key goes in and a capability comes out. Business code names the capability and never the key:

```csharp
var result = fulfilmentFactory.Create(order.Mode) switch
{
    Fulfil.Fulfil(var fulfil) => fulfil.Fulfil(parcel, order),
    Fulfil.FulfilToAddress(var fulfil) => fulfil.Fulfil(parcel, order, request.Address)
};
```

The key therefore crosses exactly one boundary — registration into the factory — and reaches nothing else.
**A key appearing outside the registration block or the factory call is the defect**, and that one-line test
covers the strategy half too: a `mode` in a handler, mapper, service, or `when` guard means the capability did
not reach far enough.

## The registration block is the partition

It is the only place a key and a capability appear together, so it is the readable declaration of how the
concern partitions the key:

```csharp
union.Case<IFulfil>(fulfil => new Fulfil.Fulfil(fulfil))
    .Use<DigitalFulfil>(FulfilmentMode.Digital)
    .Use<CollectionFulfil>(FulfilmentMode.Collection);

union.Case<IFulfilToAddress>(fulfil => new Fulfil.FulfilToAddress(fulfil))
    .Use<CourierFulfil>(FulfilmentMode.Courier, FulfilmentMode.Freight);
```

One implementation may serve several keys where the rule is identical. Completeness validation — the same
coverage check the strategy builder performs — makes **adding an enum member fail composition** rather than
throw in production for the one key nobody remembered.

**Arms grow with capabilities, not with keys.** Capabilities are bounded by real behavioural distinctions and
grow slowly; keys grow with the product. A new key registers against an existing arm and changes **zero** call
sites, where a key match would change every one. That is the whole return on the pattern, and the answer to
"won't this boilerplate multiply as the enum grows".

## Rules of the shape

- **Each arm appears exactly once in a match.** An arm matched twice — once with a `when` guard, once without
  — means the call site is performing that arm's own branching, which is what the arm was supposed to own.
- **Preconditions belong in validation, not in arm implementations.** Validate before dispatch so an arm takes
  a non-nullable parameter and its body is construction only. An implementation that opens with an `if` is
  usually a validation step that landed in the wrong layer.
- **Arms carry real payloads.** No empty cases, no members-less marker interfaces, and no nullable field
  standing in for "this case does not have one". A nullable is honest only when the value is genuinely
  *pending* rather than absent.
- **Never invent a parameter object to give differently-shaped arms one signature.** A `Candidates`/`Context`
  record whose only job is to carry the union of every arm's inputs, so each arm can ignore the fields it does
  not need, is the strategy rules applied to a union. It reintroduces exactly the discarded parameters the
  arms existed to avoid.
- **No implementation discards a parameter**, and no match arm discards with `_`. Use property access rather
  than positional deconstruction when an arm needs only part of its payload.
- **The arm's name is the case type's name.** C# 15 removes the wrapper and the arm *becomes* the type, so any
  divergence today is a rename later. Name the union so the arm can take the interface's name — a union named
  for the operation forces `Operation.Operation`.

## Shared data lives outside the union

**C# 15 unions have no shared state across cases.** Cases are independent types; "union member providers",
which would expose members common to every case, are in the proposal but are **not implemented**. The
documented workaround is a helper on the union that switches internally.

So data every case carries goes **outside** the union — a record holding the union, or one named payload
parameter per case — never on a base that cases inherit. A source generator may offer shared properties on
the union type today; using them buys convenience that the language will not honour.

Where a case genuinely has nothing of its own, that is a signal worth checking before modelling around it: an
apparently empty case often owns a fact that is currently fetched later rather than carried.

## Dunet is the interim mechanism, not the design

Until C# 15 unions ship, express these with the `Dunet` source generator: `[Union]` on an abstract partial
record with one nested partial record per arm, and its generated `Match` where exhaustiveness matters —
`Match` is compiler-checked today, a pattern `switch` is not, and a `default: throw new UnreachableException()`
is the tell that closure was assumed rather than proven.

Write the Dunet form so migration is a deletion, not a redesign: arms named as their future case types, no
shared state inside the union, and no generator-specific conveniences. Registration, coverage validation and
the capability partition are unaffected by the switch-over — **a native union closes the match; the builder
closes the registration, and neither replaces the other.**

**Implicit conversions are a per-union decision, not a house setting.** Dunet defaults them on and generates
**payload → union**, for each arm that has a single, uniquely-typed property. Enable them where every arm is a
single payload of a distinct type that no caller holds loose — an arm over an interface resolved from the
container qualifies, and there the conversion means what native assignment will mean. Disable them where any
arm wraps a type used generally elsewhere: a `Snapshot(ContractSnapshot)` arm would silently turn a bare
snapshot into that arm, with no compiler complaint, while multi-property arms get no conversion at all — one
arm implicitly reachable and the rest not is worse than none. Note this is a generator behaviour without a
native counterpart: a native union over fresh case types converts from the *case*, never from a case's
payload, so the setting is worth re-deciding at migration rather than carried across.

**The registration projection is a generator artefact.** `Case<TCase>(Func<TCase, TUnion> create)` needs a
lambda only because the wrapper record must be constructed; it tells the builder which arm wraps which
interface, which no conversion can supply. A native union declared over existing types has no wrapper, so the
projection disappears entirely. Do not "clean it up" with reflection or an `Activator` overload in the
meantime — that trades a compile-time check for brevity the migration deletes anyway.

## The anti-patterns this replaces — never do these

- **A strategy family standing in for a classification.** Three implementations that each discard a parameter,
  to choose between values the caller already holds, is a union modelled as a strategy.
- **Marker-interface arms.** A members-less interface, matched to decide which variable the caller reads, is a
  bool wearing a type.
- **A second arm for an identical signature.** Two arms with the same header are one interface and two
  implementations.
- **A `Result<T?, TError>`.** A nullable success value makes the caller unwrap twice to tell "absent" from
  "failed", and forces casts at construction. Model the absence as a case.
- **Reading common data by matching every arm.** If consumers match only to reach a field every case has, the
  shared data is in the wrong place — move it out of the union.
