---
name: http-layer
description: The client's HTTP layer — one `xApi` object per resource under the feature's `api/` folder, the response shape typed on the request generic, one HTTP-client instance per backend service created bare in the core package and enhanced with base URL, auth and tenant headers only in the app tree, and API errors resolved once at the query client's global handler with typed `meta` opt-outs, a shared retry policy, and the single legitimate exception of a route guard branching on status through the shared error seam rather than importing the HTTP library's own error helpers. Use when adding an api module or endpoint call, wiring auth or headers onto a client, writing a `try/catch` or `onError` around an API call, or adding a client for another backend.
---

# HTTP layer

## One `xApi` object per resource

`features/<feature>/api/xApi.ts` default-exports an object literal of `async` arrow methods that call the
shared client instance, type the response on the generic, destructure `{ data }`, and return it. A typed api
module kept out of components is the standard data-layer split, and it mirrors the server-side rule that an
outbound call gets a typed contract rather than hand-rolled request plumbing.

```ts
const orderApi = {
  checkout: async (orderId: number): Promise<Checkout> => {
    const { data } = await api.post<Checkout>(`/order/${orderId}/checkout`);
    return data;
  },
};
export default orderApi;
```

- Type the call at `api.get<T>` / `api.post<T>` and return `data`; the generic flows through to the
  response's `data`.
- Bodyless endpoints use the bare call with no generic. Binary reads pass the array-buffer response type and
  wrap the result in a `Blob`.
- A package-local api file that only re-exposes a shared one is a **pure re-export**, never a copy.
- Never hand-roll ad-hoc fetching where the api object expresses the call.

## One instance per backend service: bare in core, enhanced in the app tree

A multi-service backend forces one client instance **per backend the site calls**, and two layers, because
*which* backends a site may call and *with what token* is an app-level decision:

- **Core (`lib/*Client.ts`):** `create()` only — the bare instance. No base URL, no auth, no interceptors;
  the core package cannot know the site's identity.
- **App tree:** side-effect-imports the instance and enhances it through one shared fluent builder —
  `configureClient(instance, url).withAuth(getToken, onUnauthorized).withTenant(getTenantId, header)`. The
  interceptor bodies live **once** in the builder; each platform binds its auth flavour once, and a
  multi-tenant app chains the tenant header.

Only the client whose backend genuinely needs it carries a query-string serializer (an array-param format
its server binder expects); the others send no array query params.

**Litmus:** *does this touch the user's token or tenant? → the builder chain in the app tree, never
`lib/*Client.ts`.*

**The anti-patterns:** a second client for a backend that already has one — configure it, don't recreate
it — and auth wiring in the core factory.

## Errors are resolved once, at the query client

The error body is the framework's problem-details shape (RFC 9457: `{ title, detail, errors[] }`) and is
handled in **exactly one place**: the query cache's and mutation cache's global `onError`. Feature hooks and
components **do not** `try/catch` to report errors — the client already did.

Keep the platform-agnostic half — the problem-details and error-meta types, plus the policy function that
classifies an error into what to surface (or into nothing, to swallow it) — in the shared package so every
platform reuses it. Only the toast *rendering* belongs to the platform's own query client.

- **The only opt-out is typed `meta`** on the query or mutation: silence errors entirely, or declare
  expected statuses the caller handles itself, registered through the library's module augmentation.
- **Shared retry policy:** network errors and transient statuses only (`408/429/502/503/504`), capped.
- **The one legitimate inspection is control flow, not reporting** — a route guard branching on 401 to throw
  a redirect. It goes through the **shared error seam** (`isApiError(e) && e.status === 401`); the HTTP
  library's own error helpers stay confined to the shared client and its interceptor, and feature code never
  imports them.

```ts
// CORRECT — the caller expects 404 and renders its own empty state; the client stays silent
useQuery({ queryKey, queryFn, meta: { expectedErrors: [404] } });

// WRONG — a second, generic toast on top of the one the client already fired
useMutation({ mutationFn, onError: () => toast.error("Failed to save.") });
```

**The anti-patterns — each an observable double-report bug, not a style nit:**

- **A feature-local `onError` toast**, firing on top of the global handler.
- **A `try/catch` around an awaited mutation to toast** — the same double-report, spelled with a catch.
- **A validation message shown via toast** — that belongs inline beside the field, from the parse result
  (see the `write-boundary` skill).

**Litmus:** *writing a `catch` to toast an API error? Stop — the query client already did. Catch only to
change control flow.*
