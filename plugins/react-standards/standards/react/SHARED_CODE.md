# Tiered shared code

Tiers nest — a universally shared package, then per-product packages, then per-app source — and the rule is
the same at every level: **code belongs at the widest tier every consumer can legitimately run**, and
variation is injected from the owning app, never resolved inside shared code with an identity check.

**The boundary gate is mechanical:** every app's typecheck compiles the shared trees against its own tree, so
a leak into a shared tier fails a *different* app's build. Keep all of them green.

A dependency-boundary linter states the rule directly — no import from one workspace into a sibling
workspace — and catches the leak the typecheck cannot, where the import compiles but crosses a tier it had
no business crossing. **A linter that is configured but wired into no script and no CI job enforces
nothing**, and its `severity: error` reads as protection that isn't there; check that something actually
runs it before trusting the boundary to it.

## Shared is the intersection — vary it with slots, never a role check

When a shared surface must differ by product or audience, the shared code declares a **slot** and the owning
app **injects** the variation. It never learns who it is rendering for.

- A shared component takes variation as props or render slots: `AppLayout({ links })`,
  `ListingDetails({ actionsSlot })`. The seller app injects "Manage listing", the buyer app injects "Enquire" —
  the shared section never branches.
- A **fixed** affordance stays declared in shared (a card's primary button, disabled when no handler is
  supplied); only the app-specific behaviour or widget is injected. A slot is for genuine per-app variation,
  not for punting every decision to the app.
- **Identity-conditional composition is the app's job.** The app knows its audience and picks what to pass;
  shared code receives the result, already decided.

```tsx
// CORRECT — shared declares the slot; the app decides what fills it
function ListingSection({ renderActions }: { renderActions: (l: Listing) => ReactNode }) { … }

<ListingSection renderActions={(l) => <ManageListing listing={l} />} />

// WRONG — shared code inspecting identity to branch
function ListingSection({ listing }: { listing: Listing }) {
  const { user } = useAuthStore();
  return isSeller(user) ? <ManageListing … /> : <Enquire … />; // tier leak
}
```

**The anti-patterns:**

- **A role check inside shared code** to pick behaviour. This is the disease, not the cure: it makes shared
  code know its audience. Move the branch to the app and inject the result. It has caused real bugs — a
  shared widget calling one product's backend with another product's token.
- **Parking product code in a wider tier "for now."** The wider tier compiles it into apps that can never
  use it, and that is exactly how one audience gains access to another's surfaces. It goes in its owning
  tier from the first commit.
- **An app-specific route literal in a shared route contract.** Only literals *every* consumer of that tier
  registers may appear in it; anything else is injected by the owning app.

## Identity is composed, never widened

The universal user type in the widest package models only what **every** surface has: id, email,
authenticated flag, universal profile fields. A product concept — a tenant type, memberships, buyer state —
is **composed on top** by the product that owns it, never bolted onto the shared type. This mirrors the
server-side identity split, where the shared identity contract carries only the intersection and the
tenant/owner concept lives in a separate abstraction only the services with that concept depend on.

- **Shared package — base identity.** No product-specific subtypes, no product id fields, no memberships.
- **A product package — that product's identity layer, composed on the base**, populated by a
  **product-owned, typed `/me` query** returning the payload that product's backend actually sends. Product
  code reads its own fields from *this* module, never off the shared user.

```ts
// shared — base only
export interface User { id: string; email: string; isEmailVerified: boolean; }

// product package — composed on top, typed /me, no cast
export interface TenantIdentity { user: User; memberships: Membership[]; }
```

Because that product identity module holds stateful domain data — which tenant is active, what the
memberships are — it is also the feature that owns that reactive state; the two patterns land on the same
module (see `client-state`).

**The anti-patterns:**

- **Product-specific subtypes in the universal union** — a user union enumerating each product's variant with
  optional product id fields, dead weight in every bundle but one.
- **Casting extra fields off the shared user.** A helper reading a field the type does not declare is the
  shared type lying about its shape. The typed product `/me` removes the cast: the field is typed where it
  is real.
- **Two discriminants on one union** — narrowing on a role while the wire polymorphism keys on something
  else. Pick one key (see `typescript-style`).
