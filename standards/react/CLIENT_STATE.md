# Client state

## A store is private to its feature; the facade hook is the API

A store is an implementation detail of the feature that owns the client state. **Keep the store module
private:** do not export it from the feature barrel, do not import it from a component, and do not make
consumers assemble behaviour out of selectors and actions. Components consume a feature-facing **facade
hook** that returns the domain values and actions they need.

Use the library's bound-hook form — name the store `useXStore` and create it with `create<XStore>()(...)`,
reading it inside the feature facade with `useXStore((state) => state.value)`. Do not introduce a vanilla
store, a `useStore(store, selector)` call, or a separately typed state creator **merely to make the store
testable**: focused tests reset the bound store through `getState()`/`setState()`. Use a vanilla store only
where a concrete requirement cannot be met by the bound hook, and document that exception.

## Where each kind of state lives

| Kind | Home |
|---|---|
| Server state | the query cache, observed through reader hooks — see `server-state` |
| Persisted client choices (an active selection, a dismissed banner) | one private store per owning feature |
| React consumers | a facade hook composing query, store selectors, derivation, invalidation, navigation |
| Non-React consumers (route guards, request headers, logout) | one internal service/session object |
| Derived values | pure functions with explicit inputs — never stored |

- **Store client state and transitions only.** Never mirror query data into the store: it snapshots cache
  data into global state and breaks background refetch.
- **Put every transition in a named store action.** A component must not call `setState`, and a public
  helper must not be a thin spelling of `store.getState().setX(...)`.
- **Keep derivations pure by passing every input explicitly.** "Is a choice pending", "the active
  membership", "can this role do X" take their inputs as arguments. A function that reads a store, query
  client, router, storage, or browser global is infrastructure, not a pure rule.
- **Keep imperative access exceptional and cohesive.** Guards, interceptors, and logout share **one**
  internal session object, which may use `getState()` and the query client internally. Do not export a
  family of getter, setter, clear, and reconcile wrappers.
- **Direct `getState()`/`setState()` belongs only inside that internal boundary or in focused store tests.**

```ts
const useTenant = (tenantType: TenantType) => {
  const activeTenantId = useTenantStore((state) => state.activeTenantId);
  const { data: identity } = useQuery(identityQueryOptions);
  return resolveTenant(identity?.memberships ?? [], tenantType, activeTenantId);
};

const tenantSession = {
  resolve: (tenantType: TenantType) =>
    resolveTenant(cachedMemberships(), tenantType, useTenantStore.getState().activeTenantId),
};
```

A genuinely stateless, reusable rulebook — a pure lookup over a static matrix — stays a pure function
wherever it naturally lives. Co-location keeps the *stateful* domain cohesive; it does not ban pure helpers.

**Litmus:** *can a consumer import the store, or call a standalone `getX`/`setX` wrapper? Then the feature
boundary is leaking — expose the domain operation from the facade hook or the internal session.*

## The anti-patterns

- **The same derivation implemented twice** — one imperative `isXPending()` helper *and* a reactive
  `useXPending()` hook answering the same question, with a route calling both. Guaranteed drift; collapse to
  one core.
- **Raw state owners exported to consumers** — components and routes interpreting the identity cache or
  reaching into the store directly.
- **Server data copied into a store.**
- **A derived value maintained by hand as state** — an `isDirty` recomputed in every setter is derived data
  held as state; derive it from buffer-versus-source at read time.
