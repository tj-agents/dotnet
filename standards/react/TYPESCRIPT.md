# TypeScript style

The idea the whole standard rests on: **a TypeScript type identifier is local; the JSON contract is
not.** What must match the server byte-for-byte is *field names and their casing*. The type's *name*
never travels on the wire, which is why naming is the client's own decision (see the
`contract-naming` skill).

## Object shapes are `interface`; everything else is `type`

- `export interface` for every object or record shape.
- `type` for string-literal unions, discriminated-union umbrellas, template-literal types, and
  utility-derived types (`type WritableOrder = Omit<Order, "id">`).
- Extend with `interface X extends Y`, not an intersection.

The two roles then stay visually distinct at a glance.

## Casing — camelCase everywhere, no mapping step

Fields are **camelCase** and match the JSON key-for-key. A modern server framework's web defaults
serialize camelCase, so the wire is camelCase out of the box and **no client-side case conversion should
exist**.

- **A PascalCase key in a JSON body is a server bug** — something serialized outside the framework's
  configured pipeline, preserving the server language's casing. Fix it there; never add a client-side key
  rewriter.
- **The one exception is multipart `FormData`.** Multipart field names bind by property name rather than
  through the JSON policy, so uploads use the server's property casing (`"Name"`, `"Tags[0]"`).

**Litmus:** *JSON body → camelCase. `FormData` field name → the server's property name.*

## Absent values default to `undefined`

Default optional or absent values to `?: T`. Reach for `null` **only** when "deliberately set to empty" is
a distinct, acted-on state, different from "never set".

`undefined` composes with optional parameters, optional chaining, and defaults, and `JSON.stringify` drops
it, so request bodies stay clean and an omitted key deserializes to the server's absent value. **Do not
type a field `| null` merely to mirror a nullable server type** — the API may serialize an explicit
`null`, but the client contract stays `undefined` and consumers read defensively (`?? fallback`,
`!= null`), so a wire `null` reads the same as absent. Introduce `null` only when something downstream
genuinely branches on the difference.

## Server polymorphism is a discriminated union on the wire discriminator

Where the server emits a discriminator field for a polymorphic payload, model it as a discriminated union
keyed on that field, with literal values copied **exactly** from the server's declared discriminators —
that key and those values are wire contract, not a naming choice.

```ts
export interface FixedPrice { $type: "fixed"; amount: number; }
export interface TieredPrice { $type: "tiered"; unitAmount: number; minimumUnits: number; }
export type Price = FixedPrice | TieredPrice | UsagePrice;
```

Narrow with `switch (x.$type)`, and key dispatch tables off `Record<X["$type"], …>`. **Add a `never`
exhaustiveness arm so a new server subtype breaks the build rather than the runtime.** Dispatch belongs in
one table, not a switch repeated across components — see the `react-structure` skill.

**Pick exactly one discriminant.** A union carrying two candidate keys, with guards narrowing on one while
the wire polymorphism uses the other, is the violation.
