---
name: write-boundary
description: The client write boundary — every user-editable form validates its controlled-input buffer against a zod schema at submit and maps the *parsed* result, never the raw buffer, to the request type, so the parse narrows the type (removing the `!` bang and `?? fallback` that are the missing validation) and yields per-field messages rendered inline plus a real `isValid` submit gate; the schema lives in the feature's `schemas/` folder and is tied to the request with `z.infer` so drift is a compile error, and client validation is a UX affordance rather than a trust boundary. Use when building or reviewing a form, mapping a buffer to a request, seeing a non-null assertion on form data, or reporting a validation message.
---

# The write boundary

Every user-editable form validates its controlled-input buffer against a **zod** schema at submit and maps
the **parsed** result — never the raw buffer — to the `XRequest`. A form with free-typed fields and no
schema is the violation.

One schema does two jobs a hand-rolled `if` cannot do together:

- **It narrows the type at the boundary.** `parsed.data` is proven present and correctly typed, so mapping
  to the request needs no `!` bang and no `?? fallback`. **The non-null assertion *is* the missing
  validation** — a schema removes it honestly instead of asserting past it.
- **It feeds inline field errors.** `safeParse` yields per-field messages the component renders next to each
  input, plus a derived `isValid` that gates the submit button, so React state reflects *actual* validity —
  the UX a server 400 can only deliver after a round trip.

```ts
const parsed = updateOrderRequestSchema.safeParse(buffer);
if (!parsed.success) return parsed;        // the component renders parsed.error.issues inline
updateOrder(parsed.data);                  // parsed.data IS UpdateOrderRequest — no bang
```

The schema lives in `features/<feature>/schemas/`. Keep it aligned to the request with
`type XRequest = z.infer<typeof xRequestSchema>`, which makes drift a compile error, while the naming and
camelCase wire rules still hold.

**Client validation is a UX affordance, not a trust boundary.** The server re-validates every field
regardless. Never drop a server check because the client has one.

**The anti-patterns:**

- **Raw buffer to request with a `!` bang or a `?? fallback`.** The bang is the missing parse.
- **A form with free-typed fields and no schema** — no `schemas/` folder for a feature with editable inputs
  is the tell.
- **Client validation reported by a toast** instead of inline from the parse result.

**Litmus:** *a field the user can type into, with nothing parsing it before the mutation call? → add the
schema; the parsed output, not the buffer, becomes the request.*
