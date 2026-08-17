---
name: server-state
description: Server state belongs to the query library — every read is a query and every write a mutation, never a `useEffect` plus `useState` that hand-rolls caching, dedup, retries and error routing (including for a one-shot fire-on-mount action), query keys as arrays ordered generic to specific behind a per-feature factory so keys and invalidations cannot drift, and the split between a component's live input buffer and the mutation's variables, with everything constant for the hook's lifetime bound inside the hook. Use when loading or sending server data, reviewing a `useEffect` that fetches, designing query keys, wiring invalidation, or deciding what a mutation call should receive.
---

# Server state

## The query library owns all server state

Every server **read** is a query and every server **write** is a mutation, wrapped in a per-feature hook
(naming in the `react-structure` skill). **Never call an api module from a `useEffect`, and never hand-roll
`useState` + `useEffect` + a promise to load or send server data.**

The library already owns caching, request **dedup** (including a strict-mode dev double-mount), retries,
routing errors to the central error handler, and pending/error state. A fetching `useEffect` re-implements
all of that by hand and worse: it double-fires under strict mode, drops the result when the component
unmounts before the promise settles, and races on out-of-order responses. Those are the exact bugs the
library exists to remove.

**This holds even for a one-shot, fire-on-mount action** — accepting an invitation from an emailed link, for
instance. That is a query, which fires on mount and dedupes by key, not
`useEffect(() => { api.accept(id).then(navigate) }, [])`. The success side effects run at the tail of the
query function, not in a follow-up effect reacting to the result.

> **Anti-pattern:** `useEffect(() => { api.getX().then(setX) }, [])`, or an on-mount `mutate()` guarded by a
> `useRef` to dodge the strict-mode re-fire. Both are a hand-rolled reimplementation of the hook.

**Litmus:** *reading or writing server data? → a query/mutation hook. Reaching for `useEffect` or
`useState` to load or send it? → that's the violation.*

## Query keys — arrays, generic to specific, one factory per feature

Keys are arrays ordered most-generic to most-specific with the resource name first —
`["shipments", "order", orderId]` — so invalidation works by prefix. Centralize a feature's
keys in one exported factory object, so a key and its invalidations cannot drift apart across files.

## Mutation variables versus form state

- **The live controlled-input buffer is local `useState` in the component.** It is *not* an `XRequest`, and
  it **never holds server data copied out of the query cache** — copying breaks background refetch.
- On submit, the component maps its buffer to the `XRequest` and passes that as the mutation's **variables**.
- **The mutation hook binds everything constant for its lifetime** — route ids, success invalidations — and
  takes only the per-submit variables. Don't thread a fixed id through the mutation call if the hook already
  closed over it.

The parse that turns a buffer into a request is the `write-boundary` skill's subject.

**Litmus:** *changes per submit → a mutation variable. Fixed for the hook's life → bound inside the hook.*
